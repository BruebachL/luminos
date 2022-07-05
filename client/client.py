import argparse
import json
import logging
import os
import select
import socket
import sys
import time
from pathlib import Path

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout

from character.character_widget import CharacterWidget
from character.character import CharacterEncoder, decode_character
from commands.command_dice_request import CommandDiceRequest, CommandDiceRequestEncoder, decode_command_dice_request
from commands.command_listen_up import decode_listen_up, CommandListenUp
from commands.command_roll_dice import decode_command_roll_dice
from commands.info_dice_request import decode_info_dice_request, InfoDiceRequestEncoder, InfoDiceRequest
from commands.info_dice_request_decline import InfoDiceRequestDecline, InfoDiceRequestDeclineEncoder, \
    decode_info_dice_request_decline
from commands.info_roll_dice import InfoRollDice, decode_info_roll_dice
from dice.dice import Dice
from dice.dice_manager import DiceManager
from character.dice_roll_manager_layout import DiceRollManagerLayout

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 1337


class BasicWindow(QWidget):
    def __init__(self, connected_socket, player_name):
        super().__init__()

        self.player = player_name
        self.base_path = Path(os.path.dirname(Path(sys.path[0])))
        character_to_read = open(self.base_path.joinpath("character.json"), "r")
        character_json = character_to_read.read()
        character_to_read.close()
        self.character = json.loads(character_json, object_hook=decode_character)
        self.client_log_name = self.player + "_client.log"
        if os.path.exists(self.client_log_name):
            os.remove(self.client_log_name)
        if os.path.exists(self.player + "_client_sequence.log"):
            os.remove(self.player + "_client_sequence.log")
        logging.basicConfig(format="[%(asctime)s] %(message)-275s (%(module)s:%(funcName)s:%(lineno)d)",
                            handlers=[logging.FileHandler(self.client_log_name),
                                      logging.StreamHandler()],
                            datefmt='%Y-%m-%d %H:%M:%S', force=True, encoding='utf-8', level=logging.DEBUG)
        self.log = logging.getLogger(__name__)
        self.client_sequence_log = logging.Logger(self.player + " client sequence logger")
        self.client_sequence_handler = logging.FileHandler(self.player + "_client_sequence.log")
        self.client_sequence_log.addHandler(self.client_sequence_handler)

        # Network things
        self.connected_socket = connected_socket
        self.output_buffer = []
        # Connect timer to check for updates and send to server
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_for_updates_and_send_output_buffer)
        self.update_timer.start(1000)
        self.file_port = 1339

        self.setWindowTitle('DnD Tool')
        self.grid_layout = None
        self.base_layout = QTabWidget()
        self.dice_manager = DiceManager(self.base_path)
        self.base_layout.addTab(self.character_tab_ui(), "Character")
        self.base_layout.addTab(self.dice_manager, "Dice Manager")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Create the tab widget with two tabs
        self.layout.addWidget(self.dice_roll_manager_tab_ui())
        self.layout.addWidget(self.base_layout)

    def get_free_port(self):
        self.file_port = self.file_port + 1
        if self.file_port == 1350:
            self.file_port = 1339
        return self.file_port

    def decode_server_command(self, command):
        if isinstance(command, str):
            command = json.loads(command)
        match command['class']:
            case "command_roll_dice":
                self.client_sequence_log.debug("Client decoded command roll dice.")
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_command_roll_dice)
            case "info_roll_dice":
                self.client_sequence_log.debug("Client decoded info roll dice.")
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_info_roll_dice)
            case "command_dice_request":
                self.client_sequence_log.debug("Client decoded command dice request.")
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_command_dice_request)
            case "info_dice_request":
                self.client_sequence_log.debug("Client decoded info dice request.")
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_info_dice_request)
            case "info_dice_request_decline":
                self.client_sequence_log.debug("Client decoded info dice request decline.")
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_info_dice_request_decline)

    def listen_until_all_data_received(self, server):
        self.client_sequence_log.debug("Client listening to server (" + server.getpeername()[0] + ":" + str(server.getpeername()[1]) + ") ...")
        length = int.from_bytes(server.recv(12), 'big')
        self.client_sequence_log.debug("Server (" + server.getpeername()[0] + ":" + str(server.getpeername()[1]) + ") announced " + str(length) + " of data.")
        data = ""
        left_to_receive = length
        while len(data) != length:
            server.setblocking(True)
            partial_data = server.recv(left_to_receive)
            print(partial_data)
            received = str(partial_data, "UTF-8")
            data = data + received
            left_to_receive = left_to_receive - (len(received))
        server.setblocking(False)
        return data

    def announce_length_and_send(self, server, output):
        server.sendall(len(output).to_bytes(12, 'big'))
        self.client_sequence_log.debug("Announced " + str(len(output)) + " to Server (" + server.getpeername()[0] + ":" + str(server.getpeername()[1]) + ")")
        server.sendall(output)
        self.client_sequence_log.debug("Sent all to Server (" + server.getpeername()[0] + ":" + str(server.getpeername()[1]) + ")")

    def check_for_updates_and_send_output_buffer(self):
        read_sockets, write_sockets, error_sockets = select.select(
            [self.connected_socket], [self.connected_socket], [self.connected_socket])

        for read_sock in read_sockets:
            # incoming message from remote server
            received_command = self.listen_until_all_data_received(read_sock)
            self.log.debug("Received: " + received_command)
            cmd = json.loads(received_command, object_hook=self.decode_server_command)
            if not received_command:
                print('\nDisconnected from server')
                break
            else:
                if received_command != "None":
                    print(cmd)
                    self.process_server_response(cmd)

        for write_sock in write_sockets:
            if len(self.output_buffer) > 0:
                for output in self.output_buffer:
                    self.log.debug("Sent: " + str(output, "UTF-8"))
                    self.announce_length_and_send(write_sock, output)
                self.output_buffer.clear()

    def process_server_response(self, response):
        match response:
            case InfoRollDice():
                self.client_sequence_log.debug("Processing dice roll information from server.")
                dice_not_available = self.dice_manager.check_if_dice_available(response.dice_skins)
                if dice_not_available is not None:
                    self.client_sequence_log.debug("Couldn't find dice " + str(dice_not_available))
                    for dice in dice_not_available:
                        dice_request = json.dumps(CommandDiceRequest(dice, self.get_free_port()),
                                                  cls=CommandDiceRequestEncoder)
                        self.client_sequence_log.debug("Sending dice request.")
                        self.announce_length_and_send(self.connected_socket, bytes(dice_request, "UTF-8"))
                        not_ready_to_receive = True
                        while not_ready_to_receive:
                            read_sockets, write_sockets, error_sockets = select.select(
                                [self.connected_socket], [self.connected_socket], [self.connected_socket])
                            for read_sock in read_sockets:
                                info_response = self.listen_until_all_data_received(read_sock)
                                info_response = self.decode_server_command(info_response)
                                if isinstance(info_response, InfoDiceRequest):
                                    self.client_sequence_log.debug("Received Info Dice Request.")
                                    file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    file_host = host
                                    not_connected = True
                                    while not_connected:
                                        try:
                                            file_sock.connect((file_host, info_response.port))
                                            not_connected = False
                                            self.client_sequence_log.debug("Connected to " + str(file_host) + ":" + str(info_response.port))
                                        except:
                                            print("Waiting for connection")
                                    length = info_response.length
                                    self.client_sequence_log.debug("Expecting to receive " + str(length) + "on " + str(file_host) + ":" + str(info_response.port))
                                    data = b''
                                    left_to_receive = length
                                    while len(data) != length:
                                        file_sock.setblocking(True)
                                        received = file_sock.recv(left_to_receive)
                                        data = data + received
                                        left_to_receive = left_to_receive - (len(received))
                                    file_sock.setblocking(False)
                                    file_to_write = open(
                                        self.dice_manager.base_resource_path.joinpath(info_response.image_path), "bw")
                                    file_to_write.write(data)
                                    self.client_sequence_log.debug(
                                        "Wrote file with " + str(len(data)) + " from " + str(file_host) + ":" + str(
                                            info_response.port))
                                    self.dice_manager.add_dice(
                                        Dice(info_response.name, info_response.group, info_response.image_path, False))
                                    self.dice_manager.update_layout()
                                    not_ready_to_receive = False
                                else:
                                    self.client_sequence_log.debug("Waiting for dice request but received another command in the meantime.")
                                    self.process_server_response(info_response)
                self.grid_layout.label.add_dice_roll(response.roll_value, response.dice_skins)
                self.grid_layout.listview.insertItem(0, str(response))
            case CommandListenUp():
                listen_up = json.loads(str(response), object_hook=decode_listen_up)
                file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                file_host = host
                self.client_sequence_log.debug("Listening up on (" + file_host + ":" + str(listen_up.port) + ") ...")
                file_sock.connect((file_host, listen_up.port))
                self.client_sequence_log.debug("Connected on (" + file_host + ":" + str(listen_up.port) + "). Waiting for " + listen_up.length + " of data.")
                length = listen_up.length
                data = b''
                left_to_receive = length
                while len(data) != length:
                    file_sock.setblocking(True)
                    received = file_sock.recv(left_to_receive)
                    data = data + received
                    left_to_receive = left_to_receive - (len(received))
                file_sock.setblocking(False)
                file_to_write = open(self.base_path.joinpath(listen_up.file_name), "bw")
                file_to_write.write(data)
            case CommandDiceRequest():
                cmd = json.loads(str(response), object_hook=decode_command_dice_request)
                self.client_sequence_log.debug("Received request for dice (" + cmd.name + ")")
                dice_to_return = self.dice_manager.get_dice_for_name(cmd.name)
                if dice_to_return is None:
                    self.client_sequence_log.debug("Have to decline dice request for dice (" + cmd.name + ")")
                    self.announce_length_and_send(self.connected_socket, bytes(
                        json.dumps(InfoDiceRequestDecline(cmd.name), cls=InfoDiceRequestDeclineEncoder), "UTF-8"))
                else:
                    self.client_sequence_log.debug("Fulfilling dice request for dice (" + cmd.name + ")")
                    self.announce_length_and_send(self.connected_socket, bytes(json.dumps(
                        InfoDiceRequest(dice_to_return.name, dice_to_return.group, dice_to_return.image_path),
                        cls=InfoDiceRequestEncoder), "UTF-8"))
                    file = open(dice_to_return.image_path, "rb")
                    file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    file_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    file_socket.bind((self.host, 1340))
                    self.client_sequence_log.debug("Returning dice request on " + self.host + ":" + str(1340))
                    file_socket.listen(5)
                    file_client, file_address = file_socket.accept()
                    file_socket.settimeout(60)
                    file_client.sendfile(file)
                    file_socket.close()


    def dice_roll_manager_tab_ui(self):
        """Create the General page UI."""
        generalTab = QWidget()
        self.grid_layout = DiceRollManagerLayout(self.output_buffer, player, self.dice_manager)
        generalTab.setLayout(self.grid_layout)
        return generalTab

    def character_tab_ui(self):
        """Create the Character page UI."""
        return CharacterWidget(player, self.character, self.dice_manager, self.output_buffer)

def save_to_file(character_to_write):
    f = open("../character.json", "w")
    f.write(character_to_write)
    f.close()


if __name__ == '__main__':
    try:
        time.sleep(1)
        parser = argparse.ArgumentParser(description='Homebrew DnD Tool.')
        parser.add_argument('--ip', help='Server IP')
        parser.add_argument('--name', help='Character name')
        args = parser.parse_args()
        if args.ip is not None:
            host = args.ip
        if args.name is not None:
            player = args.name
        else:
            player = "Dummy"
        app = QApplication(sys.argv)
        sock.connect((host, port))
        sock.setblocking(False)
        window = BasicWindow(sock, player)
        window.show()
        sys.exit(app.exec_())
    finally:
        print("saving to file")
        save_to_file(json.dumps(window.character, cls=CharacterEncoder))
        window.dice_manager.save_to_file()
