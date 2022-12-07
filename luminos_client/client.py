import argparse
import json
import logging
import os
import random
import select
import socket
import sys
import time
from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QHBoxLayout, QSplashScreen

from audio.audio_info import AudioInfo
from audio.audio_manager import AudioManager
from character.character_manager import CharacterManager
from character.character import CharacterEncoder
from luminos_client.admin_panel import TabbedClientView, AdminPanel
from clues.clue import Clue
from clues.clue_manager import ClueManager
from commands.client_info import ClientInfo
from commands.command import decode_command, InfoRollDice, CommandListenUp, InfoDiceRequestDecline, \
    InfoDiceFile, CommandEncoder, CommandFileRequest, CommandRevealClue, CommandRevealMapOverlay, InfoFileRequest, \
    CommandPlayAudio, CommandUpdateClientInfo, CommandQueryConnectedClients
from config import Configuration
from dice.dice import Dice
from dice.dice_manager import DiceManager
from dice.dice_roll_manager_layout import DiceRollManagerLayout
from map.base_map_info import BaseMapInfo
from map.map_manager import MapManager
from map.overlay_map_info import OverlayMapInfo
from utils.string_utils import fix_up_json_string


class BasicWindow(QWidget):
    def __init__(self, server_ip, server_port, admin_client):
        super().__init__()
        self.base_path = Path(os.path.dirname(Path(sys.path[0])))
        self.client_id = random.randint(0, 1337)
        self.admin_client = admin_client
        self.config_path = Path.joinpath(self.base_path, 'config.cfg')
        self.config = Configuration(self.config_path)
        self.player = self.config.config['Character Name'][0]

        # Splash screen setup
        self.splash_screen = QSplashScreen(QPixmap(str(Path("resources").joinpath(Path("splash_screen.png")))))
        self.splash_screen.setWindowFlags(self.splash_screen.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.splash_screen.show()

        # Logging setup
        self.splash_screen.showMessage("Setting up logging...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter,
                                       QtCore.Qt.white)
        self.log = self.setup_logger(self.player + "_client.log")
        self.log.addHandler(logging.StreamHandler())
        self.client_sequence_log = self.setup_logger(self.player + "_client_sequence.log")

        # Network setup
        self.splash_screen.showMessage("Connecting to server...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter,
                                       QtCore.Qt.white)
        if server_ip is None:
            server_ip = self.config.config['IP'][0]
        if server_port is None:
            server_port = self.config.config['Port'][0]
        self.server_ip = server_ip
        self.server_port = server_port
        self.connected_socket = None
        self.attempt_reconnect_to_server()
        self.output_buffer = []
        self.connected_clients = []
        self.output_buffer.append(bytes(fix_up_json_string(json.dumps(CommandUpdateClientInfo(ClientInfo(self.client_id, self.player + "#" + str(self.client_id), "0.3", "Connected.")), cls=CommandEncoder)), "UTF-8"))
        self.output_buffer.append(bytes(fix_up_json_string(json.dumps(CommandQueryConnectedClients([]),
                                                                      cls=CommandEncoder)), "UTF-8"))
        # Connect timer to check for updates and send to server
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_for_updates_and_send_output_buffer)
        self.update_timer.start(1000)
        self.file_port = 1339

        # Layout setup
        self.splash_screen.showMessage("Initializing UI...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter,
                                       QtCore.Qt.white)
        self.setWindowTitle('DnD Tool')
        self.base_layout = QTabWidget()
        self.audio_manager = None
        self.character_manager = None
        self.dice_manager = None
        self.map_manager = None
        self.clue_manager = None
        self.dice_roll_manager = None
        self.admin_panel = None
        self.layout = QHBoxLayout()

        # Actually build the layout
        self.build_layout()

        # Finalize splash screen
        self.splash_screen.showMessage("Done! Launching...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter,
                                       QtCore.Qt.white)
        time.sleep(1.5)
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

    ####################################################################################################################
    #                                                UI Housekeeping                                                   #
    ####################################################################################################################

    def build_layout(self):
        QWidget().setLayout(self.layout)
        self.layout = QHBoxLayout()
        self.base_layout = QTabWidget()

        # Create the managers
        self.dice_manager = DiceManager(self, self.base_path)
        self.character_manager = CharacterManager(self, self.base_path)
        self.map_manager = MapManager(self, self.base_path)
        self.clue_manager = ClueManager(self, self.base_path)
        self.dice_roll_manager = DiceRollManagerLayout(self.output_buffer, self.player, self.dice_manager)
        self.audio_manager = AudioManager(self, self.base_path)
        self.admin_panel = AdminPanel(self, self.connected_clients)

        # Create the main function tabs
        self.base_layout = self.character_manager.generate_ui_tabs(self.base_layout)
        self.base_layout.addTab(self.map_manager, "Map")
        self.base_layout.addTab(self.clue_manager, "Clues")
        self.base_layout.addTab(self.audio_manager, "Audio")
        self.base_layout.addTab(self.dice_manager, "Dice Manager")
        if self.admin_client:
            self.base_layout.addTab(self.admin_panel, "Admin")

        # Create the main UI screen with two split layouts
        self.layout.addWidget(self.dice_roll_manager)
        self.layout.addWidget(self.base_layout)


        self.setLayout(self.layout)
        self.repaint()


    ####################################################################################################################
    #                                                Network (General)                                                 #
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
        connection_attempts = 0
        #progress_bar = QProgressBar(self.splash_screen)
        # Can't do this, might need a layout for the splashscreen
        #progress_bar.setWindowFlags(progress_bar.windowFlags() | QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter | QtCore.Qt.WindowStaysOnTopHint)
        #progress_bar.setRange(0,0)
        #progress_bar.move(250, 150)
        #progress_bar.show()
        while not_connected:
            if connection_attempts < 10:
                connection_attempts += 1
                try:
                    self.log.debug("Attempting to connect to {}:{}".format(self.server_ip, self.server_port))
                    self.connected_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.connected_socket.connect((self.server_ip, self.server_port))
                    self.connected_socket.setblocking(False)
                    self.log.debug("Connected to {}:{}".format(self.server_ip, self.server_port))
                    # self.announce_length_and_send(self.connected_socket, bytes(self.submodule_name, 'UTF-8'))
                    not_connected = False
                except socket.error:
                    self.log.debug("Failed reconnection attempt to {}:{}".format(self.server_ip, self.server_port))
                    time.sleep(1)
            else:
                self.splash_screen.showMessage("Cannot connect to server. Exiting ...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter,
                                               QtCore.Qt.white)
                time.sleep(2)
                sys.exit(1)

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
        server.setblocking(True)
        length = int.from_bytes(server.recv(12), 'big')
        print("Server length: {}".format(length))
        self.client_sequence_log.debug(
            "Server (" + server.getpeername()[0] + ":" + str(server.getpeername()[1]) + ") announced " + str(
                length) + " of data.")
        data = ""
        left_to_receive = length
        while len(data) != length:
            print(len(data))
            server.setblocking(True)
            partial_data = server.recv(left_to_receive)
            print(partial_data)
            if partial_data is not [] or partial_data is not None:
                try:
                    while partial_data[0] != 123:
                        partial_data = partial_data[1:]
                except IndexError as e:
                    print(partial_data)
                    print(len(partial_data))
                    print(type(partial_data))
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
            case CommandQueryConnectedClients():
                self.connected_clients = response.connected_client_infos
                self.admin_panel.connected_clients = self.connected_clients
                self.admin_panel.update_layout()
            case InfoRollDice():
                self.client_sequence_log.debug("Processing dice roll information from server.")
                dice_not_available = self.dice_manager.check_if_dice_available(response.dice_skins)
                if dice_not_available is not None:
                    self.client_sequence_log.debug("Couldn't find dice " + str(dice_not_available))
                    for dice in dice_not_available:
                        self.request_dice_from_server(dice)
                self.dice_roll_manager.dice_roll_viewer.add_dice_roll(response.roll_value, response.dice_skins)
                self.dice_roll_manager.text_history_viewer.insertItem(0, str(response))
                #self.build_layout()
            case CommandRevealClue():
                clue_to_reveal = self.clue_manager.get_clue_for_hash(response.file_hash)
                if clue_to_reveal is None:
                    self.request_clue_from_server(response.file_hash)
                clue_to_reveal = self.clue_manager.get_clue_for_hash(response.file_hash)
                clue_to_reveal.revealed = response.revealed
                self.clue_manager.update_layout()
            case CommandRevealMapOverlay():
                map_overlay_to_reveal = self.map_manager.get_map_info_for_hash(response.file_hash)
                if map_overlay_to_reveal is None:
                    self.request_map_from_server(response.file_hash)
                else:
                    map_overlay_to_reveal.revealed = response.revealed
                self.map_manager.update_layout()
            case CommandPlayAudio():
                audio_to_play = self.audio_manager.get_audio_info_for_hash(response.file_hash)
                if audio_to_play is None:
                    self.request_audio_from_server(response.file_hash)
                self.audio_manager.play_audio(response.file_hash)
            case CommandListenUp():
                listen_up = json.loads(str(response), object_hook=decode_command)
                self.receive_file_from_server(listen_up.length, listen_up.port, listen_up.file_name)
            case CommandFileRequest():
                cmd = json.loads(str(response), object_hook=decode_command)
                self.client_sequence_log.debug("Received request for dice (" + cmd.display_name + ")")
                dice_to_return = self.dice_manager.get_dice_for_hash(cmd.display_name)
                if dice_to_return is None:
                    self.client_sequence_log.debug("Have to decline dice request for dice (" + cmd.display_name + ")")
                    self.announce_length_and_send(self.connected_socket, bytes(
                        json.dumps(InfoDiceRequestDecline(cmd.display_name), cls=CommandEncoder), "UTF-8"))
                else:
                    self.client_sequence_log.debug("Fulfilling dice request for dice (" + cmd.display_name + ")")
                    self.announce_length_and_send(self.connected_socket, bytes(json.dumps(
                        InfoDiceFile(dice_to_return.checksum, dice_to_return.group),
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

    def request_audio_from_server(self, clue):
        data, info_response = self.request_file_from_server(clue, "audio:stinger")
        path = self.write_file_to_path(data, self.audio_manager.base_resource_path, info_response)
        self.audio_manager.audio_clips.append(AudioInfo(info_response.file_hash, path, info_response.file_info.display_name))
        self.audio_manager.file_hash_map = self.audio_manager.populate_file_hash_map()
        self.audio_manager.detect_unknown_audios()
        self.audio_manager.update_layout()
        print("Received audio.")

    def request_clue_from_server(self, clue):
        data, info_response = self.request_file_from_server(clue, "image:clue")
        path = self.write_file_to_path(data, self.clue_manager.base_resource_path, info_response)
        self.clue_manager.clues.append(Clue(info_response.file_hash, path, info_response.file_info.display_name, info_response.file_info.revealed))
        self.clue_manager.update_layout()
        print("Received clue.")

    def request_dice_from_server(self, dice):
        data, info_response = self.request_file_from_server(dice, "image:dice")
        print(str(info_response.name) + "." + str(info_response.extension))
        path = self.write_file_to_path(data, self.dice_manager.base_resource_path, info_response)
        self.dice_manager.add_dice(Dice(info_response.file_info.display_name, info_response.file_info.group, path, False))
        self.dice_manager.update_layout()
        print("Received dice.")

    def request_map_from_server(self, map_hash):
        data, info_response = self.request_file_from_server(map_hash, "image:map")
        print(str(info_response.name) + "." + str(info_response.extension))
        path = self.write_file_to_path(data, self.map_manager.base_resource_path, info_response)
        if info_response.file_info.base_map:
            self.map_manager.base_maps.append(BaseMapInfo(path, info_response.file_hash, []))
            print("Received Base Map.")
        else:
            self.map_manager.get_active_map().overlays.append(OverlayMapInfo(path, info_response.file_hash, info_response.file_info.revealed))
            print("Received Map Overlay.")
        self.map_manager.update_layout()


    def write_file_to_path(self, data, path, info_response):
        file_to_write = open(path.joinpath(str(info_response.name) + "." + str(info_response.extension)), "bw")
        file_to_write.write(data)
        return path.joinpath(str(info_response.name) + "." + str(info_response.extension))

    def request_file_from_server(self, file_hash, file_type):
        file_request = json.dumps(CommandFileRequest(file_hash, file_type, self.get_free_port()), cls=CommandEncoder)
        self.client_sequence_log.debug("Sending file request.")
        self.announce_length_and_send(self.connected_socket, bytes(file_request, "UTF-8"))
        info_response = self.listen_until_all_data_received(self.connected_socket)
        info_response = self.decode_server_command(info_response)
        while not isinstance(info_response, InfoFileRequest):
            self.process_server_response(info_response)
            info_response = self.listen_until_all_data_received(self.connected_socket)
            info_response = self.decode_server_command(info_response)
        while True:
            read_sockets, write_sockets, error_sockets = select.select(
                [self.connected_socket], [self.connected_socket], [self.connected_socket])
            for read_sock in read_sockets:
                listen_up_response = self.listen_until_all_data_received(read_sock)
                listen_up_response = self.decode_server_command(listen_up_response)
                self.client_sequence_log.debug("This should be a listen up...")
                if isinstance(listen_up_response, CommandListenUp):
                    self.client_sequence_log.debug("Received Listen Up.")
                    # Make sure this is correct info response
                    file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    file_host = self.server_ip
                    not_connected = True
                    while not_connected:
                        try:
                            file_sock.connect((file_host, listen_up_response.port))
                            not_connected = False
                            self.client_sequence_log.debug(
                                "Connected to " + str(file_host) + ":" + str(listen_up_response.port))
                        except:
                            print("Waiting for connection")
                    length = listen_up_response.length
                    self.client_sequence_log.debug(
                        "Expecting to receive " + str(length) + "on " + str(file_host) + ":" + str(listen_up_response.port))
                    data = b''
                    left_to_receive = length
                    while len(data) != length:
                        file_sock.setblocking(True)
                        received = file_sock.recv(left_to_receive)
                        data = data + received
                        left_to_receive = left_to_receive - (len(received))
                    file_sock.setblocking(False)
                    return data, info_response
                else:
                    self.client_sequence_log.debug(
                        "Waiting for file request but received another command in the meantime.")
                    self.process_server_response(listen_up_response)

    def save_managers(self):
        self.audio_manager.save_to_file()
        self.dice_manager.save_to_file()
        self.character_manager.save_to_file()
        self.map_manager.save_to_file()
        self.clue_manager.save_to_file()
        # self.dice_roll_manager.save_to_file()


if __name__ == '__main__':
    try:
        time.sleep(1)
        parser = argparse.ArgumentParser(description='Homebrew DnD Tool.')
        parser.add_argument('--ip', help='Server IP (Default: localhost)')
        parser.add_argument('--port', help='Server port (Default: 1337)', default=1337, type=int, action="store")
        parser.add_argument('--admin', help='Launch as admin luminos_client', action="store_true")
        args = parser.parse_args()
        app = QApplication(sys.argv)
        window = BasicWindow(args.ip, args.port, args.admin)
        sys.exit(app.exec_())
    finally:
        print("saving to file")
        window.save_managers()
        print(fix_up_json_string(json.dumps(window.character_manager.character, cls=CharacterEncoder, separators=(',', ':'), indent=4, ensure_ascii=False)))
