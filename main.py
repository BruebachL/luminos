import hashlib
import json
import logging
import os
import socket
import sys
import threading
import traceback

from PyQt5.QtWidgets import QApplication

from audio.audio_manager import AudioManager
from clues.clue_manager import ClueManager
from commands.command import CommandRollDice, CommandFileRequest, InfoDiceRequestDecline, CommandEncoder, \
    InfoDiceFile, CommandListenUp, decode_command, InfoFileRequest, InfoMapFile, InfoClueFile, CommandRevealMapOverlay, \
    CommandRevealClue, InfoAudioFile, CommandPlayAudio
from dice.dice import Dice
from dice.dice_manager import DiceManager
from map.base_map_info import BaseMapInfo
from map.map_manager import MapManager
from server import gamestate
from utils.string_utils import fix_up_json_string

base_path = sys.path[0]
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


def get_free_port(port):
    port = port + 1
    if port == 1350:
        port = 1339
    return port


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        app = QApplication(sys.argv)
        self.game_state = gamestate.GameState("asdf")
        self.clue_manager = ClueManager(None, base_path)
        self.dice_manager = DiceManager(None, base_path)
        self.map_manager = MapManager(None, base_path)
        self.audio_manager = AudioManager(None, base_path)
        self.connected_clients = []

    #server_sequence_log.debug("Client (" + client.getpeername()[0] + "")
    def execute_command(self, client, game_state, command):
        cmd = json.loads(command, object_hook=decode_command)
        match cmd:
            case CommandRollDice():
                server_sequence_log.debug("Rolling some dice for Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ")")
                return game_state.add_dice_roll(cmd)
            case CommandFileRequest():
                print("File requested.")
                self.fulfill_file_request(client, cmd)
                # We don't broadcast this to all clients, so we return none here
                return None
            case CommandRevealMapOverlay():
                return json.dumps(cmd, cls=CommandEncoder)
            case CommandRevealClue():
                return json.dumps(cmd, cls=CommandEncoder)
            case CommandPlayAudio():
                return json.dumps(cmd, cls=CommandEncoder)
            case _:
                print("Unknown command:")
                print(cmd)

    def get_requested_file_from_managers(self, file_hash, file_type):
        file_to_return, file_info_detail = None, None
        match file_type:
            case "audio:stinger":
                file_to_return = self.audio_manager.get_path_for_hash(file_hash)
                audio_info = self.audio_manager.get_audio_info_for_hash(file_hash)
                file_info_detail = InfoAudioFile(audio_info.display_name)
            case "image:clue":
                file_to_return = self.clue_manager.get_path_for_hash(file_hash)
                clue_info = self.clue_manager.get_clue_for_hash(file_hash)
                file_info_detail = InfoClueFile(clue_info.display_name, clue_info.revealed)
            case "image:dice":
                file_to_return = self.dice_manager.get_path_for_hash(file_hash)
                dice_info = self.dice_manager.get_dice_for_hash(file_hash)
                file_info_detail = InfoDiceFile(dice_info.display_name, dice_info.group)
            case "image:map":
                file_to_return = self.map_manager.get_path_for_hash(file_hash)
                map_info = self.map_manager.get_map_info_for_hash(file_hash)
                if isinstance(map_info, BaseMapInfo):
                    file_info_detail = InfoMapFile(True, True)
                else:
                    file_info_detail = InfoMapFile(False, map_info.revealed)
        return file_to_return, file_info_detail

    def get_file_information(self, file_path):
        file = open(file_path, "rb")
        file_length = os.path.getsize(file_path)
        file_name = file_path
        file_data = file.read()
        file_hash = hashlib.sha256(file_data).hexdigest()
        file.seek(0)
        return file, InfoFileRequest('.'.join(os.path.split(file_path)[1].split('.')[:-1]),
                                                                       file_path.split('.')[-1], None,
                                                                       len(file_data), file_hash, None)
        
    def fulfill_file_request(self, client, file_request):
        file_to_return, file_info_detail = self.get_requested_file_from_managers(file_request.file_hash, file_request.file_type)
        print("Got requested file:")
        print(file_to_return)
        # Check if we actually have the requested file
        if file_to_return is None:
            print("Didn't have requested file. Requesting from clients...")
            raise Exception
        # Gather file information
        file, file_info = self.get_file_information(file_to_return)
        file_info.file_info = file_info_detail
        file_info.file_type = file_request.file_type
        print(fix_up_json_string(json.dumps(file_info, cls=CommandEncoder)))
        # Send it
        self.announce_length_and_send(client,
                                      bytes(fix_up_json_string(json.dumps(file_info, cls=CommandEncoder)), "UTF-8"))
        print("Sent announcement.")
        threading.Thread(target=self.send_file_to_client,
                         args=(file, file_info.file_length, file_to_return, client, file_request.port)).start()

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
        return Dice(response.display_name, response.group, response.image_path, False)

    def request_dice_from_client(self, client_to_request_from, dice_to_request):
        dice_request = CommandFileRequest(dice_to_request, 1340)
        self.announce_length_and_send(client_to_request_from, bytes(json.dumps(dice_request, cls=CommandEncoder), "UTF-8"))
        response = self.listen_until_all_data_received(client_to_request_from)
        command = json.loads(str(response, "UTF-8"), object_hook=decode_command)
        if isinstance(command, InfoDiceRequestDecline):
            return None
        if isinstance(command, InfoDiceFile):
            return self.receive_dice_from_client(client_to_request_from, command)
        return None

    def request_dice_from_clients(self, requesting_client, dice_to_request):
        for client in self.connected_clients:
            if client != requesting_client:
                returned_dice = self.request_dice_from_client(client, dice_to_request)
                if returned_dice is not None:
                    return returned_dice

    def fulfill_dice_request(self, dice_checksum, client, port):
        server_sequence_log.debug("Client (" + client.getpeername()[0] + ":" + str(
            client.getpeername()[1]) + ") requests some dice (" + dice_checksum + ").")
        dice_to_return = self.dice_manager.get_dice_for_hash(dice_checksum)
        if dice_to_return is None:
            server_sequence_log.debug("Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[
                                                                                           1]) + ") requested a dice (" + dice_checksum + ") that we didn't have. Requesting from other clients...")
            requested_dice = self.request_dice_from_clients(client, dice_checksum)
            if requested_dice is not None:
                server_sequence_log.debug(
                    "Someone had the dice (" + dice_checksum + ") that Client (" + client.getpeername()[0] + ":" + str(
                        client.getpeername()[1]) + ") requested.")
                self.dice_manager.add_dice(requested_dice)
            else:
                server_sequence_log.debug(
                    "No one had the dice (" + dice_checksum + ") that Client (" + client.getpeername()[
                        0] + ") requested. Declining request.")
                return json.dumps(InfoDiceRequestDecline(dice_to_return), cls=CommandEncoder)
        server_sequence_log.debug(
            "Fulfilling dice request (" + dice_checksum + ") for Client (" + client.getpeername()[0] + ":" + str(
                client.getpeername()[1]) + ")")

        server_sequence_log.debug(
            "Launched thread for  (" + dice_to_return.image_path + ") for Client (" + client.getpeername()[0] + ":" + str(client.getpeername()[1]) + ") on port " + str(port))
        file, file_info = self.get_file_information(dice_to_return.image_path)
        file_info.file_info = InfoDiceFile(dice_to_return.display_name, dice_to_return.group)
        self.announce_length_and_send(client, bytes(fix_up_json_string(json.dumps(file_info, cls=CommandEncoder)), "UTF-8"))
        threading.Thread(target=self.send_file_to_client, args=(file, file_info.file_length, dice_to_return.image_path, client, port)).start()

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
        not_connected = True
        while not_connected:
            try:
                file_socket.bind((self.host, port))
                not_connected = False
            except OSError as e:
                port = get_free_port(port)
        self.announce_length_and_send(client, bytes(json.dumps(CommandListenUp(port, file_length, file_name), cls=CommandEncoder), "UTF-8"))
        file_socket.listen(5)
        while True:
            file_client, file_address = file_socket.accept()
            file_socket.settimeout(60)
            threading.Thread(target=self.send_file, args=(file_client, file_socket, file)).start()
            break


    # TODO: Not sure if we can use sendfile here.
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
                if not data:
                    raise ConnectionError('Client disconnected')
                server_log.debug(data)
                response = self.execute_command(client, self.game_state, data)
                if response:
                    # Set the response to echo back the received data
                    self.send_to_clients(bytes(str(response), "UTF-8"))
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
