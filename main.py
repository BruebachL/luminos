import json
import logging
import os
import socket
import sys
import threading
import traceback

from PyQt5.QtWidgets import QApplication

from commands.command import CommandRollDice, CommandDiceRequest, InfoDiceRequestDecline, CommandEncoder, \
    InfoDiceRequest, CommandListenUp, decode_command
from dice.dice import Dice
from dice.dice_manager import DiceManager
from server import gamestate
base_path = sys.path[0] + "/"
lock = threading.Lock()

if os.path.exists('example.log'):
    os.remove('example.log')
if os.path.exists('server.log'):
    os.remove('server.log')
if os.path.exists('server_sequence.log'):
    os.remove('server_sequence.log')
logging.basicConfig(format="[%(asctime)s] %(message)-275s (%(module)s:%(funcName)s:%(lineno)d)",
                    handlers=[logging.FileHandler("example.log"),
                              logging.StreamHandler()],
                    datefmt='%Y-%m-%d %H:%M:%S', force=True, encoding='utf-8', level=logging.DEBUG)
log = logging.getLogger(__name__)
server_log = logging.Logger("server logger")
server_handler = logging.FileHandler("server.log")
server_log.addHandler(server_handler)
server_sequence_log = logging.Logger("server sequence logger")
server_sequence_handler = logging.FileHandler("server_sequence.log")
server_sequence_log.addHandler(server_sequence_handler)


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        app = QApplication(sys.argv)
        self.game_state = gamestate.GameState("asdf")
        self.dice_manager = DiceManager(base_path)
        self.connected_clients = []

    #server_sequence_log.debug("Client (" + client.getpeername()[0] + "")
    def execute_command(self, client, game_state, command):
        cmd = json.loads(command, object_hook=decode_command)
        match cmd:
            case CommandRollDice():
                server_sequence_log.debug("Rolling some dice for Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ")")
                return game_state.add_dice_roll(cmd)
            case CommandDiceRequest():
                server_sequence_log.debug("Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ") requests some dice (" + cmd.name + ").")
                dice_to_return = self.dice_manager.get_dice_for_name(cmd.name)
                if dice_to_return is None:
                    server_sequence_log.debug("Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ") requested a dice (" + cmd.name + ") that we didn't have. Requesting from other clients...")
                    requested_dice = self.request_dice_from_clients(client, cmd.name)
                    if requested_dice is not None:
                        server_sequence_log.debug("Someone had the dice (" + cmd.name + ") that Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ") requested.")
                        self.dice_manager.add_dice(requested_dice)
                    else:
                        server_sequence_log.debug(
                            "No one had the dice (" + cmd.name + ") that Client (" + client.getpeername()[
                                0] + ") requested. Declining request.")
                        return json.dumps(InfoDiceRequestDecline(dice_to_return), cls=CommandEncoder)
                server_sequence_log.debug(
                    "Fulfilling dice request (" + cmd.name + ") for Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ")")
                self.fulfill_dice_request(dice_to_return, client, cmd.port)
                return json.dumps(InfoDiceRequest(dice_to_return.name, dice_to_return.group, dice_to_return.image_path.split("/")[len(dice_to_return.image_path.split("/")) - 1], os.path.getsize(dice_to_return.image_path), cmd.port), cls=CommandEncoder)

    def receive_dice_from_client(self, client_to_receive_from, info_dice_request):
        response = info_dice_request
        file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_host = client_to_receive_from.getpeername()
        file_sock.connect((file_host, 1340))
        data = b''
        while True:
            buf = file_sock.recv(1024)
            if not buf:
                break
            data += buf
        file_to_write = open(response.image_path, "bw")
        file_to_write.write(data)
        return Dice(response.name, response.group, response.image_path, False)

    def request_dice_from_client(self, client_to_request_from, dice_to_request):
        dice_request = CommandDiceRequest(dice_to_request, 1340)
        self.announce_length_and_send(client_to_request_from, bytes(json.dumps(dice_request, cls=CommandEncoder), "UTF-8"))
        response = self.listen_until_all_data_received(client_to_request_from)
        command = json.loads(str(response, "UTF-8"), object_hook=decode_command)
        if isinstance(command, InfoDiceRequestDecline):
            return None
        if isinstance(command, InfoDiceRequest):
            return self.receive_dice_from_client(client_to_request_from, command)
        return None

    def request_dice_from_clients(self, requesting_client, dice_to_request):
        for client in self.connected_clients:
            if client != requesting_client:
                returned_dice = self.request_dice_from_client(client, dice_to_request)
                if returned_dice is not None:
                    return returned_dice

    def fulfill_dice_request(self, dice, client, port):
        file = open(dice.image_path, "rb")
        file_length = os.path.getsize(dice.image_path)
        file_name = dice.image_path
        server_sequence_log.debug(
            "Launched thread for  (" + dice.image_path + ") for Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ") on port " + str(port))
        threading.Thread(target=self.send_file_to_client, args=(file, file_length, file_name, client, port)).start()

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            self.connected_clients.append(client)
            threading.Thread(target=self.listen_to_client, args=(client, address)).start()

    def send_to_clients(self, response):
        for connected_client in self.connected_clients:
            self.announce_length_and_send(connected_client, response)

    def send_file_to_clients(self, file, clients, port):
        for client in clients:
            self.send_file_to_client(file, client, port)

    def send_file_to_client(self, file, file_length, file_name, client, port):
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        file_socket.bind((self.host, port))
        self.announce_length_and_send(client, bytes(json.dumps(CommandListenUp(port, file_length, file_name), cls=CommandEncoder), "UTF-8"))
        file_socket.listen(5)
        while True:
            file_client, file_address = file_socket.accept()
            file_socket.settimeout(60)
            threading.Thread(target=self.send_file, args=(file_client, file_socket, file)).start()
            break

    def send_file(self, file_client, file_socket, file):
        server_sequence_log.debug(
            "Sending file to Client (" + file_client.getpeername()[0] + ":" + str(
                file_client.getpeername()[1]) + ")")
        file_client.sendfile(file)
        file_socket.close()


    def announce_length_and_send(self, client, output):
        server_sequence_log.debug("Announcing length of " + str(len(output)) + " to Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ")")
        client.sendall(len(output).to_bytes(12, 'big'))
        server_sequence_log.debug("Sending to Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ")")
        client.sendall(output)
        log.debug("Sent " + str(output, "UTF-8") + " with length " + str(len(output)) + " to " + str(client.getpeername()))

    def listen_until_all_data_received(self, client):
        server_sequence_log.debug("Listening to Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ") ...")
        length = int.from_bytes(client.recv(12), 'big')
        server_sequence_log.debug("Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ") announced " + str(length) + " of data.")
        data = ""
        left_to_receive = length
        while len(data) != length:
            received = str(client.recv(left_to_receive), "UTF-8")
            data = data + received
            left_to_receive = left_to_receive - (len(received))
            server_sequence_log.debug("Received " + str(len(received)) + " from Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ") and have " + str(left_to_receive) + " left to receive.")
        log.debug("Received " + data + " with length " + str(length))
        return data

    def listen_to_client(self, client, address):
        while True:
            try:
                data = self.listen_until_all_data_received(client)
                server_log.debug(data)
                response = self.execute_command(client, self.game_state, data)
                if data:
                    # Set the response to echo back the received data
                    self.send_to_clients(bytes(str(response), "UTF-8"))
                else:
                    raise ConnectionError('Client disconnected')
            except:
                traceback.print_exc()
                self.connected_clients.remove(client)
                client.close()
                return False


if __name__ == "__main__":
    while True:
        port_num = 1337
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    ThreadedServer(socket.gethostname(), port_num).listen()
