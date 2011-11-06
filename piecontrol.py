import re
import os
import subprocess

class CommandLineAction():
    def execute(self, command):
        subprocess.call(command, shell=True)

class PieFind:

    def __init__(self, config):
        self.ignored_dirs = config.get_ignored_dirs()
        self.key_command_mappings = config.get_key_command_mappings()

    def find_files(self, baseDir, searchstring, results=[]):
        try:
            dirList = os.listdir(baseDir)
        except OSError:
            dirList = []

        subDirs = []
        for item in dirList:
            path = os.path.join(baseDir, item)
            if os.path.isfile(path):
                if self.matches(searchstring, item):
                    if path.startswith('./'):
                        path = path[2:]
                    results.append(path)
            else:
                if item not in self.ignored_dirs:
                    subDirs.append(path)

        for subDir in subDirs:
            self.find_files(subDir, searchstring, results)

        return results

    def matches(self, searchstring, item):
        return re.search(searchstring, item, re.IGNORECASE)

    def has_key_mapping(self, key):
        return key in self.key_command_mappings

    def get_command(self, key):
        return self.key_command_mappings[key]

