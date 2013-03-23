# -*- coding: utf-8 -*-
import re
import os
import stat
import subprocess
import sys

class CommandLineAction():
    def execute(self, command):
        subprocess.call(command, shell=True)

class PieFind:

    def __init__(self, config):
        self.ignored_dirs = config.get_ignored_dirs()
        self.key_command_mappings = config.get_key_command_mappings()
        self.ignore_hidden = config.ignore_hidden()

    def find_files(self, baseDir, searchstring, results=[]):
        try:
            dirList = os.listdir(baseDir)
        except OSError:
            dirList = []

        subDirs = []
        for item in dirList:
            if self.ignore_hidden and self.is_hidden(item):
                continue

            path = os.path.join(baseDir, item)
            if not self.isgroupreadable(path):
                sys.stderr.write("pie: '%s': Permission denied\n" % path)
                continue

            # if symlink, add only if target is a file
            if os.path.islink(path):
                target = os.path.realpath(path)
                if os.path.isfile(target):
                    results.append(self.cleanpath(path))
            elif os.path.isfile(path):
                if self.matches(searchstring, item):
                    results.append(self.cleanpath(path))
            else:
                if item not in self.ignored_dirs:
                    subDirs.append(path)

        for subDir in subDirs:
            self.find_files(subDir, searchstring, results)

        return results

    # See: http://stackoverflow.com/questions/1861836
    def isgroupreadable(self, filepath):
        # TODO: avoid try/except
        try:
            st = os.stat(filepath)
            return bool(st.st_mode & stat.S_IRGRP)
        except:
            return False

    def is_hidden(self, item):
        return item.startswith('./') is False and item.startswith('.')

    def cleanpath(self, path):
        if path.startswith('./'):
            path = path[2:]
        return path

    def matches(self, searchstring, item):
        return re.search(searchstring, item, re.IGNORECASE)

    def has_key_mapping(self, key):
        return key in self.key_command_mappings

    def get_command(self, key):
        return self.key_command_mappings[key]

