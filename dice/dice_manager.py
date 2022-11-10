import json
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from dice.dice import Dice
from dice.dice_group import DiceGroup, DiceGroupEncoder, decode_dice_group
from dice.dice_group_widget import DiceGroupWidget
from os import listdir
from os.path import isfile, join


class DiceManager(QWidget):
    def __init__(self, basePath):
        super().__init__()
        self.base_path = Path(basePath)
        self.base_resource_path = Path.joinpath(self.base_path, Path("resources")).joinpath(Path("dice_pictures"))
        self.dice_config_file = Path.joinpath(self.base_path, "dice.json")
        self.dice_groups = []
        self.use_dice = []
        self.read_from_file()
        self.populate_use_dice()
        self.layout = QVBoxLayout()
        self.tab_layout = QTabWidget()
        self.layout.addWidget(self.tab_layout)
        self.add_dice_group_widgets(self.tab_layout)
        self.setLayout(self.layout)
        if "Ungrouped" in [dice_group.name for dice_group in self.dice_groups]:
            for dice_group in self.dice_groups:
                if dice_group.name == "Ungrouped":
                    dice_group.dice.extend(self.get_all_dice())
        else:
            self.dice_groups.append(DiceGroup("Ungrouped", self.get_all_dice(), Path("resources")).joinpath(Path("dice_pictures")))

    def update_layout(self):
        self.save_to_file()
        self.dice_groups = []
        self.use_dice = []
        self.read_from_file()
        self.populate_use_dice()
        QWidget().setLayout(self.layout)
        new_layout = QVBoxLayout()
        self.setLayout(new_layout)
        self.layout = new_layout
        new_tab_layout = QTabWidget()
        new_layout.addWidget(new_tab_layout)
        self.add_dice_group_widgets(new_tab_layout)

        if "Ungrouped" in [dice_group.name for dice_group in self.dice_groups]:
            for dice_group in self.dice_groups:
                if dice_group.name == "Ungrouped":
                    dice_group.dice.extend(self.get_all_dice())
        else:
            self.dice_groups.append(DiceGroup("Ungrouped", self.get_all_dice(), Path("resources")).joinpath(Path("dice_pictures")))

    def add_dice(self, dice_to_add):
        for dice_group in self.dice_groups:
            if dice_group.name == dice_to_add.group:
                dice_group.dice.append(dice_to_add)
                return
        self.dice_groups.append(DiceGroup(dice_to_add.group, [dice_to_add], dice_to_add.image_path))

    def check_if_dice_available(self, dice_to_check):
        not_available = []
        for dice in dice_to_check:
            if self.get_dice_for_name(dice) is None:
                if dice not in not_available:
                    not_available.append(dice)
        if len(not_available) > 0:
            return not_available
        else:
            return None

    def get_dice_for_name(self, look_for):
        for dice_group in self.dice_groups:
            for dice in dice_group.dice:
                if dice.name == look_for:
                    return dice

    def get_all_dice(self):
        not_found_dice = []
        onlyfiles = [f for f in listdir(self.base_resource_path) if isfile(join(self.base_resource_path, f))]
        for file in onlyfiles:
            dice = [x for x in self.dice_groups]
            file_paths = [[x.image_path for x in y.dice] for y in dice]
            dice_file_paths = [[x for x in dice_file_path] for dice_file_path in file_paths]
            all_dice_file_paths = []
            for path in dice_file_paths:
                all_dice_file_paths.extend(path)
            if str(self.base_resource_path.joinpath(Path(str(file)))) not in all_dice_file_paths:
                not_found_dice.append(Dice(file, "Ungrouped", self.base_resource_path.joinpath(Path(str(file))), True))
        return not_found_dice

    def read_from_file(self):
        file = open(self.dice_config_file, "r")
        lines = file.readlines()
        for line in lines:
            self.dice_groups.append(json.loads(line, object_hook=decode_dice_group))

    def save_to_file(self):
        file = open(self.dice_config_file, "w")
        for dice_group in self.dice_groups:
            print("Writing file group ", str(json.dumps(dice_group, cls=DiceGroupEncoder) + "\n"))
            file.write(json.dumps(dice_group, cls=DiceGroupEncoder) + "\n")
        file.close()

    def populate_use_dice(self):
        for group in self.dice_groups:
            for dice in group.dice:
                if dice.use:
                    self.use_dice.append(dice)

    def add_dice_group_widget(self, layout, dice_group):
        layout.addTab(DiceGroupWidget(dice_group, self), dice_group.name)

    def add_dice_group_widgets(self, layout):
        for dice_group in self.dice_groups:
            self.add_dice_group_widget(layout, dice_group)

    def dice_group_change(self, dice_widget):
        for dice_group in self.dice_groups:
            if dice_group.name == dice_widget.dice.group:
                if dice_widget.dice.name in [x.name for x in dice_group.dice]:
                    dice_group.dice.remove(dice_widget.dice)
                    if len(dice_group.dice) == 0:
                        self.dice_groups.remove(dice_group)
        need_new_group = True
        for dice_group in self.dice_groups:
            if dice_group.name == dice_widget.line_edit.text():
                dice_group.dice.append(dice_widget.dice)
                dice_widget.dice.group = dice_group.name
                need_new_group = False
        if need_new_group:
            dice_widget.dice.group = dice_widget.line_edit.text()
            self.dice_groups.append(DiceGroup(dice_widget.line_edit.text(), [dice_widget.dice], dice_widget.dice.image_path))
