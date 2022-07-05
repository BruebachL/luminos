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
player = "Ascor"
base_path = Path(os.path.dirname(Path(sys.path[0])))
character_to_read = open(base_path.joinpath("character.json"), "r")
character_json = character_to_read.read()
character_to_read.close()
character = json.loads(character_json, object_hook=decode_character)
client_log_name = player + "_client.log"
if os.path.exists(client_log_name):
    os.remove(client_log_name)
logging.basicConfig(format="[%(asctime)s] %(message)-275s (%(module)s:%(funcName)s:%(lineno)d)",
                    handlers=[logging.FileHandler(client_log_name),
                              logging.StreamHandler()],
                    datefmt='%Y-%m-%d %H:%M:%S', force=True, encoding='utf-8', level=logging.DEBUG)
log = logging.getLogger(__name__)


class BasicWindow(QWidget):
    def __init__(self, connected_socket):
        super().__init__()

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
        self.dice_manager = DiceManager(base_path)
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
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_command_roll_dice)
            case "info_roll_dice":
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_info_roll_dice)
            case "command_dice_request":
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_command_dice_request)
            case "info_dice_request":
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_info_dice_request)
            case "info_dice_request_decline":
                return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                                  object_hook=decode_info_dice_request_decline)

    def listen_until_all_data_received(self, server):
        length = int.from_bytes(server.recv(12), 'big')
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
        server.sendall(output)

    def check_for_updates_and_send_output_buffer(self):
        read_sockets, write_sockets, error_sockets = select.select(
            [self.connected_socket], [self.connected_socket], [self.connected_socket])

        for read_sock in read_sockets:
            # incoming message from remote server
            received_command = self.listen_until_all_data_received(read_sock)
            log.debug("Received: " + received_command)
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
                    log.debug("Sent: " + str(output, "UTF-8"))
                    self.announce_length_and_send(write_sock, output)
                self.output_buffer.clear()

    def process_server_response(self, response):
        match response:
            case InfoRollDice():
                dice_not_available = self.dice_manager.check_if_dice_available(response.dice_skins)
                if dice_not_available is not None:
                    for dice in dice_not_available:
                        dice_request = json.dumps(CommandDiceRequest(dice, self.get_free_port()),
                                                  cls=CommandDiceRequestEncoder)
                        self.announce_length_and_send(self.connected_socket, bytes(dice_request, "UTF-8"))
                        not_ready_to_receive = True
                        while not_ready_to_receive:
                            read_sockets, write_sockets, error_sockets = select.select(
                                [self.connected_socket], [self.connected_socket], [self.connected_socket])
                            for read_sock in read_sockets:
                                info_response = self.listen_until_all_data_received(read_sock)
                                info_response = self.decode_server_command(info_response)
                                if isinstance(info_response, InfoDiceRequest):
                                    file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    file_host = host
                                    not_connected = True
                                    while not_connected:
                                        try:
                                            file_sock.connect((file_host, info_response.port))
                                            not_connected = False
                                        except:
                                            print("Waiting for connection")
                                    length = info_response.length
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
                                    self.dice_manager.add_dice(
                                        Dice(info_response.name, info_response.group, info_response.image_path, False))
                                    self.dice_manager.update_layout()
                                    not_ready_to_receive = False
                                else:
                                    self.process_server_response(info_response)
                self.grid_layout.label.add_dice_roll(response.roll_value, response.dice_skins)
                self.grid_layout.listview.insertItem(0, str(response))
            case CommandListenUp():
                listen_up = json.loads(str(response), object_hook=decode_listen_up)
                file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                file_host = host
                file_sock.connect((file_host, listen_up.port))
                length = listen_up.length
                data = b''
                left_to_receive = length
                while len(data) != length:
                    file_sock.setblocking(True)
                    received = file_sock.recv(left_to_receive)
                    data = data + received
                    left_to_receive = left_to_receive - (len(received))
                file_sock.setblocking(False)
                file_to_write = open(base_path.joinpath(listen_up.file_name), "bw")
                file_to_write.write(data)
            case CommandDiceRequest():
                cmd = json.loads(str(response), object_hook=decode_command_dice_request)
                dice_to_return = self.dice_manager.get_dice_for_name(cmd.name)
                if dice_to_return is None:
                    self.announce_length_and_send(self.connected_socket, bytes(
                        json.dumps(InfoDiceRequestDecline(cmd.name), cls=InfoDiceRequestDeclineEncoder), "UTF-8"))
                else:
                    self.announce_length_and_send(self.connected_socket, bytes(json.dumps(
                        InfoDiceRequest(dice_to_return.name, dice_to_return.group, dice_to_return.image_path),
                        cls=InfoDiceRequestEncoder), "UTF-8"))
                    file = open(dice_to_return.image_path, "rb")
                    file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    file_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    file_socket.bind((self.host, 1340))
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
        return CharacterWidget(player, character, self.dice_manager, self.output_buffer)

def save_to_file(character_to_write):
    f = open("../character.json", "w")
    f.write(character_to_write)
    f.close()


if __name__ == '__main__':
    try:
        time.sleep(1)
        parser = argparse.ArgumentParser(description='Homebrew DnD Tool.')
        parser.add_argument('--ip', help='Server IP')
        args = parser.parse_args()
        if args.ip is not None:
            host = args.ip
        app = QApplication(sys.argv)
        sock.connect((host, port))
        sock.setblocking(False)
        window = BasicWindow(sock)
        window.show()
        sys.exit(app.exec_())
    finally:
        print("saving to file")
        save_to_file(json.dumps(character, cls=CharacterEncoder))
        window.dice_manager.save_to_file()
