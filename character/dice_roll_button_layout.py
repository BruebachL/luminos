import json
import random

from PyQt5.QtWidgets import QGridLayout, QPushButton

from commands.command import CommandRollDice, CommandEncoder


class DiceRollButtonLayout(QGridLayout):
    def __init__(self, output_buffer, player, dice_manager):
        super().__init__()
        self.output_buffer = output_buffer
        self.dice_manager = dice_manager
        self.player = player
        self.add_buttons()
        self.dice_to_use = []
        if len(self.dice_manager.use_dice) > 0:
            self.dice_to_use.append(
                self.dice_manager.use_dice[random.randrange(len(self.dice_manager.use_dice))].name)

    def add_buttons(self):
        roll_button = QPushButton()
        roll_d2_button = QPushButton()
        roll_d4_button = QPushButton()
        roll_d6_button = QPushButton()
        roll_d8_button = QPushButton()
        roll_d10_button = QPushButton()
        roll_d20_button = QPushButton()
        roll_d2_button.clicked.connect(self.roll_d2)
        roll_d4_button.clicked.connect(self.roll_d4)
        roll_d6_button.clicked.connect(self.roll_d6)
        roll_d8_button.clicked.connect(self.roll_d8)
        roll_d10_button.clicked.connect(self.roll_d10)
        roll_d20_button.clicked.connect(self.roll_d20)
        roll_button.clicked.connect(self.roll_dice)
        roll_button.setText("Roll!")
        roll_d2_button.setText("Roll a D2")
        roll_d4_button.setText("Roll a D4")
        roll_d6_button.setText("Roll a D6")
        roll_d8_button.setText("Roll a D8")
        roll_d10_button.setText("Roll a D10")
        roll_d20_button.setText("Roll a D20")
        
        self.addWidget(roll_d2_button, 1, 1)
        self.addWidget(roll_d4_button, 1, 2)
        self.addWidget(roll_d6_button, 1, 3)
        self.addWidget(roll_d8_button, 2, 1)
        self.addWidget(roll_d10_button, 2, 2)
        self.addWidget(roll_d20_button, 2, 3)
        self.addWidget(roll_button, 3, 2)

    def roll_dice(self):
        # data = 4
        # self.output_buffer.append(bytes(json.dumps(CommandRollDice(self.player, data, 20, "the hell of it", 10, 0, dice_to_use), cls=CommandRollDiceEncoder), "UTF-8"))
        self.dice_manager.update_layout()

    def roll_d2(self):
        self.output_buffer.append(bytes(
            json.dumps(CommandRollDice(self.player, 1, 2, "the hell of it", 10, 0, self.dice_to_use),
                       cls=CommandEncoder), "UTF-8"))

    def roll_d4(self):
        self.output_buffer.append(bytes(
            json.dumps(CommandRollDice(self.player, 1, 4, "the hell of it", 10, 0, self.dice_to_use),
                       cls=CommandEncoder), "UTF-8"))

    def roll_d6(self):
        self.output_buffer.append(bytes(
            json.dumps(CommandRollDice(self.player, 1, 6, "the hell of it", 10, 0, self.dice_to_use),
                       cls=CommandEncoder), "UTF-8"))

    def roll_d8(self):
        self.output_buffer.append(bytes(
            json.dumps(CommandRollDice(self.player, 1, 8, "the hell of it", 10, 0, self.dice_to_use),
                       cls=CommandEncoder), "UTF-8"))

    def roll_d10(self):
        self.output_buffer.append(bytes(
            json.dumps(CommandRollDice(self.player, 1, 10, "the hell of it", 10, 0, self.dice_to_use),
                       cls=CommandEncoder), "UTF-8"))

    def roll_d20(self):
        self.output_buffer.append(bytes(
            json.dumps(CommandRollDice(self.player, 3, 20, "the hell of it", 10, 0, self.dice_to_use),
                       cls=CommandEncoder), "UTF-8"))

