import hashlib
import os
from os import listdir
from os.path import join, isfile
from pathlib import Path

from PyQt5.QtWidgets import QWidget


class UpdateManager(QWidget):

    def __init__(self, parent, base_path):
        super().__init__(parent)
        self.parent = parent
        self.base_path = base_path
        self.folders = self.get_folders()
        self.folder_file_hash_maps = {}
        self.generate_folder_file_hash_map()
        #if self.parent is not None:
            # self.check_for_updated_files(self.folder_file_hash_maps)



    def get_absolute_path_for_hash(self, hash_to_get):
        for folder in self.folder_file_hash_maps:
            for file in self.folder_file_hash_maps[folder]:
                if hash_to_get == file:
                    temp_join_path = self.folder_file_hash_maps[folder][file]
                    cleaned_base_name = self.base_path
                    if cleaned_base_name.endswith('\\') or cleaned_base_name.endswith('/'):
                        cleaned_base_name = cleaned_base_name[:-1]
                    temp_join_path = temp_join_path.replace("/" + os.path.split(cleaned_base_name)[1] + "/", '')
                    temp_join_path = temp_join_path.replace("\\" + os.path.split(cleaned_base_name)[1] + "\\", '')
                    print(temp_join_path)
                    return os.path.join(self.base_path, temp_join_path)

    def get_relative_folder_path_for_hash(self, hash_to_get):
        for folder in self.folder_file_hash_maps:
            for file in self.folder_file_hash_maps[folder]:
                if hash_to_get == file:
                    temp_join_path = self.folder_file_hash_maps[folder][file]
                    while temp_join_path[0] == '/' or temp_join_path[0] == '\\':
                        temp_join_path = temp_join_path[1:]
                    return os.path.split(os.path.join(*Path(temp_join_path).parts[1:]))[0]

    def generate_folder_file_hash_map(self):
        self.folder_file_hash_maps = {}
        for folder in self.folders:
            self.folder_file_hash_maps[
                folder.replace(os.path.split(str(self.base_path))[0], '')] = self.populate_file_hash_map_for_folder(
                folder)
        return self.folder_file_hash_maps

    def check_for_updated_files(self, external_hash_map):
        local_hash_map = self.generate_folder_file_hash_map()
        missing_locally, missing_externally = self.compare_folder_hash_maps(local_hash_map, external_hash_map)
        # TODO: Check if files are in both missing locally and missing externally (File was modified.)
        print(missing_locally)
        print(missing_externally)
        for file in missing_locally:
            print("Locally missing server file: " + str(file))
            self.window().request_file_update_from_server(file)
        for file in missing_externally:
            # self.prompt_deletion(file)
            print("Server is missing local file: " + str(file))

    def compare_folder_hash_maps(self, local_hash_map, external_hash_map):
        all_files_local_folder = {}
        all_files_external_folder = {}
        print(local_hash_map)
        for folder in local_hash_map:
            for file in local_hash_map[folder]:
                all_files_local_folder[file] = local_hash_map[folder][file]
        for folder in external_hash_map:
            for file in external_hash_map[folder]:
                all_files_external_folder[file] = external_hash_map[folder][file]
        missing_locally = {}
        missing_externally = {}
        for file in all_files_local_folder:
            if file not in all_files_external_folder:
                missing_externally[file] = all_files_local_folder[file]
        for file in all_files_external_folder:
            if file not in all_files_local_folder:
                missing_locally[file] = all_files_external_folder[file]
        return missing_locally, missing_externally

    def populate_file_hash_map_for_folder(self, path):
        file_hash_map = {}
        onlyfiles = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
        for file_path in onlyfiles:
            if not self.is_filtered(file_path):
                with open(file_path, 'rb') as file:
                    file_hash_map[hashlib.sha256(file.read()).hexdigest()] = str(file_path.replace(os.path.split(str(self.base_path))[0], ''))
        return file_hash_map

    def is_filtered(self, path):
        filtered = [".git", "__pycache__", "venv", "env", ".idea", "egg-info", ".log", ".json", ".cfg", "resources"]
        for filter in filtered:
            if filter in path:
                return True
        return False

    def get_folders(self):
        dir_paths = os.walk(self.base_path)

        filtered_paths = []
        for dir_path in dir_paths:
            if not self.is_filtered(dir_path[0]):
                filtered_paths.append(dir_path[0])
        return filtered_paths


    def get_folder_or_file(self, path, folder_list, file_list):
        if isfile(path):
            file_list.append(path)
        else:
            folder_list.append(path)
        return folder_list, file_list