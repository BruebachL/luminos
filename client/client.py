import argparse
import json
import logging
import os
import select
import socket
import sys
import time
from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QHBoxLayout, QSplashScreen

from character.character_widget import CharacterWidget
from character.character import CharacterEncoder, decode_character
from commands.command import decode_command, InfoRollDice, CommandListenUp, CommandDiceRequest, InfoDiceRequestDecline, \
    InfoDiceRequest, CommandEncoder
from dice.dice import Dice
from dice.dice_manager import DiceManager
from character.dice_roll_manager_layout import DiceRollManagerLayout


class BasicWindow(QWidget):
    def __init__(self, server_ip, server_port, player_name):
        super().__init__()

        self.close_splash_timer = QTimer()
        self.close_splash_timer.timeout.connect(self.close_splash)
        self.splash_screen = self.show_splash()

        # Character setup
        self.player = player_name
        self.base_path = Path(os.path.dirname(Path(sys.path[0])))
        character_to_read = open(self.base_path.joinpath("character.json"), "r")
        character_json = character_to_read.read()
        character_to_read.close()
        self.character = json.loads(character_json, object_hook=decode_character)

        # Logging setup
        self.log = self.setup_logger(self.player + "_client.log")
        self.log.addHandler(logging.StreamHandler())
        self.client_sequence_log = self.setup_logger(self.player + "_client_sequence.log")

        # Network setup
        if server_ip is None:
            server_ip = socket.gethostname()
        if server_port is None:
            server_port = 1337
        self.server_ip = server_ip
        self.server_port = server_port
        self.connected_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_socket.connect((server_ip, server_port))
        self.connected_socket.setblocking(False)
        self.output_buffer = []
        # Connect timer to check for updates and send to server
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_for_updates_and_send_output_buffer)
        self.update_timer.start(1000)
        self.file_port = 1339

        # Layout setup
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


    def show_splash(self):
        pixmap = QPixmap('resources/splash_screen.png')
        splash_screen = QSplashScreen(pixmap)
        splash_screen.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        splash_screen.show()
        self.close_splash_timer.start(3000)

        return splash_screen


    def close_splash(self):
        self.splash_screen.close()
        self.show()


    def setup_logger(self, log_name):
        if os.path.exists(log_name):
            os.remove(log_name)
        logger = logging.Logger(log_name)
        handler = logging.FileHandler(log_name)
        formatter = logging.Formatter(fmt="[%(asctime)s] %(message)-160s (%(module)s:%(funcName)s:%(lineno)d)",
                                             datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


    def dice_roll_manager_tab_ui(self):
        """Create the General page UI."""
        generalTab = QWidget()
        self.grid_layout = DiceRollManagerLayout(self.output_buffer, player, self.dice_manager)
        generalTab.setLayout(self.grid_layout)
        return generalTab

    def character_tab_ui(self):
        """Create the Character page UI."""
        return CharacterWidget(player, self.character, self.dice_manager, self.output_buffer)

    ####################################################################################################################
    #                                                Network                                                           #
    ####################################################################################################################

    # Main Send/Receive Loop
    def check_for_updates_and_send_output_buffer(self):
        read_sockets, write_sockets, error_sockets = select.select(
            [self.connected_socket], [self.connected_socket], [self.connected_socket])

        for read_sock in read_sockets:
            # incoming message from remote server
            received_command = self.listen_until_all_data_received(read_sock)
            self.log.debug("Received: " + received_command)
            if not received_command:
                print('\nDisconnected from server')
                self.attempt_reconnect_to_server()
                break
            else:
                cmd = json.loads(received_command, object_hook=self.decode_server_command)
                if received_command != "None":
                    print(cmd)
                    self.process_server_response(cmd)

        for write_sock in write_sockets:
            if len(self.output_buffer) > 0:
                for output in self.output_buffer:
                    self.log.debug("Sent: " + str(output, "UTF-8"))
                    self.announce_length_and_send(write_sock, output)
                self.output_buffer.clear()

    def attempt_reconnect_to_server(self):
        not_connected = True
        while not_connected:
            try:
                self.log.debug("Attempting to connect to {}:{}".format(self.server_ip, self.server_port))
                self.connected_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connected_socket.connect((self.server_ip, self.server_port))
                self.log.debug("Connected to {}:{}".format(self.server_ip, self.server_port))
                #self.announce_length_and_send(self.connected_socket, bytes(self.submodule_name, 'UTF-8'))
                not_connected = False
            except socket.error:
                self.log.debug("Failed reconnection attempt to {}:{}".format(self.server_ip, self.server_port))
                time.sleep(1)

    def get_free_port(self):
        self.file_port = self.file_port + 1
        if self.file_port == 1350:
            self.file_port = 1339
        return self.file_port

    ####################################################################################################################
    #                                                Network (Receive)                                                 #
    ####################################################################################################################
    def listen_until_all_data_received(self, server):
        self.client_sequence_log.debug(
            "Client listening to server (" + server.getpeername()[0] + ":" + str(server.getpeername()[1]) + ") ...")
        length = int.from_bytes(server.recv(12), 'big')
        self.client_sequence_log.debug(
            "Server (" + server.getpeername()[0] + ":" + str(server.getpeername()[1]) + ") announced " + str(
                length) + " of data.")
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

    def receive_file_from_server(self, length, port, file_name):
        file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_host = self.server_ip
        self.client_sequence_log.debug("Listening up on (" + file_host + ":" + str(port) + ") ...")
        file_sock.connect((file_host, port))
        self.client_sequence_log.debug("Connected on (" + file_host + ":" + str(
            port) + "). Waiting for " + length + " of data.")
        data = b''
        left_to_receive = length
        while len(data) != length:
            file_sock.setblocking(True)
            received = file_sock.recv(left_to_receive)
            data = data + received
            left_to_receive = left_to_receive - (len(received))
        file_sock.setblocking(False)
        file_to_write = open(self.base_path.joinpath(file_name), "bw")
        file_to_write.write(data)

    def process_server_response(self, response):
        match response:
            case InfoRollDice():
                self.client_sequence_log.debug("Processing dice roll information from server.")
                dice_not_available = self.dice_manager.check_if_dice_available(response.dice_skins)
                if dice_not_available is not None:
                    self.client_sequence_log.debug("Couldn't find dice " + str(dice_not_available))
                    for dice in dice_not_available:
                        self.request_dice_from_server(dice)
                self.grid_layout.label.add_dice_roll(response.roll_value, response.dice_skins)
                self.grid_layout.listview.insertItem(0, str(response))
            case CommandListenUp():
                listen_up = json.loads(str(response), object_hook=decode_command)
                self.receive_file_from_server(listen_up.length, listen_up.port, listen_up.file_name)
            case CommandDiceRequest():
                cmd = json.loads(str(response), object_hook=decode_command)
                self.client_sequence_log.debug("Received request for dice (" + cmd.name + ")")
                dice_to_return = self.dice_manager.get_dice_for_name(cmd.name)
                if dice_to_return is None:
                    self.client_sequence_log.debug("Have to decline dice request for dice (" + cmd.name + ")")
                    self.announce_length_and_send(self.connected_socket, bytes(
                        json.dumps(InfoDiceRequestDecline(cmd.name), cls=CommandEncoder), "UTF-8"))
                else:
                    self.client_sequence_log.debug("Fulfilling dice request for dice (" + cmd.name + ")")
                    self.announce_length_and_send(self.connected_socket, bytes(json.dumps(
                        InfoDiceRequest(dice_to_return.name, dice_to_return.group, dice_to_return.image_path),
                        cls=CommandEncoder), "UTF-8"))
                    file = open(dice_to_return.image_path, "rb")
                    self.client_sequence_log.debug("Returning dice request on " + self.server_ip + ":" + str(1340))
                    self.send_file_to_server(file, 1340)

    def decode_server_command(self, command):
        if isinstance(command, str):
            command = json.loads(command)
        return json.loads(str(command).replace('\'', '\"').replace('True', 'true').replace('False', 'false'),
                          object_hook=decode_command)

    ####################################################################################################################
    #                                                Network (Send)                                                    #
    ####################################################################################################################

    def announce_length_and_send(self, server, output):
        server.sendall(len(output).to_bytes(12, 'big'))
        self.client_sequence_log.debug(
            "Announced " + str(len(output)) + " to Server (" + server.getpeername()[0] + ":" + str(
                server.getpeername()[1]) + ")")
        server.sendall(output)
        self.client_sequence_log.debug(
            "Sent all to Server (" + server.getpeername()[0] + ":" + str(server.getpeername()[1]) + ")")

    def send_file_to_server(self, file, file_port):
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        file_socket.bind((self.server_ip, file_port))
        file_socket.listen(5)
        file_client, file_address = file_socket.accept()
        file_socket.settimeout(60)
        file_client.sendfile(file)
        file_socket.close()


    def request_dice_from_server(self, dice):
        dice_request = json.dumps(CommandDiceRequest(dice, self.get_free_port()),
                                  cls=CommandEncoder)
        self.client_sequence_log.debug("Sending dice request.")
        self.announce_length_and_send(self.connected_socket, bytes(dice_request, "UTF-8"))
        not_ready_to_receive = True
        while not_ready_to_receive:
            read_sockets, write_sockets, error_sockets = select.select(
                [self.connected_socket], [self.connected_socket], [self.connected_socket])
            for read_sock in read_sockets:
                info_response = self.listen_until_all_data_received(read_sock)
                info_response = self.decode_server_command(info_response)
                if isinstance(info_response, CommandListenUp):
                    self.client_sequence_log.debug("Received Info Dice Request.")
                    file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    file_host = self.server_ip
                    not_connected = True
                    while not_connected:
                        try:
                            file_sock.connect((file_host, info_response.port))
                            not_connected = False
                            self.client_sequence_log.debug(
                                "Connected to " + str(file_host) + ":" + str(info_response.port))
                        except:
                            print("Waiting for connection")
                    length = info_response.length
                    self.client_sequence_log.debug(
                        "Expecting to receive " + str(length) + "on " + str(file_host) + ":" + str(info_response.port))
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
                    self.client_sequence_log.debug(
                        "Waiting for dice request but received another command in the meantime.")
                    self.process_server_response(info_response)

def save_to_file(character_to_write):
    f = open("../character.json", "w")
    f.write(character_to_write)
    f.close()


if __name__ == '__main__':
    try:
        time.sleep(1)
        parser = argparse.ArgumentParser(description='Homebrew DnD Tool.')
        parser.add_argument('--ip', help='Server IP (Default: localhost)')
        parser.add_argument('--port', help='Server port (Default: 1337)', default=1337, type=int, action="store")
        parser.add_argument('--name', help='Character name')
        args = parser.parse_args()
        if args.name is not None:
            player = args.name
        else:
            player = "Dummy"
        app = QApplication(sys.argv)
        window = BasicWindow(args.ip, args.port, player)
        sys.exit(app.exec_())
    finally:
        print("saving to file")
        save_to_file(json.dumps(window.character, cls=CharacterEncoder))
        window.dice_manager.save_to_file()
