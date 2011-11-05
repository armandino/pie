#!/usr/bin/env python

import argparse
import ConfigParser
import logging
import os
import re
import subprocess
import sys
import urwid

from abc import ABCMeta, abstractmethod

# TODO: fix error - python pie.py /tmp/

class PieConfig:
    CONFIG_FILE = '~/.pie'

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.expanduser(self.CONFIG_FILE))

    def get_key_command_mappings(self):
        action_map = {}
        try:
            actions = self.config.items('KeyMappings')
            for action in actions:
                action_name = action[0]
                action_cmd = action[1]
                action_map[action_name] = action_cmd
        except:
            pass
        return action_map


    def get_ignored_dirs(self):
        ignored = []
        try:
            value = self.config.get('Ignore', 'directories')
            ignored = [x.strip() for x in value.split(',')]
        except:
            pass
        return ignored


class PieUI(urwid.ListWalker):

    PAGE_SCROLL_SIZE = 10
    
    logging.basicConfig(filename='/tmp/pie.log', level=logging.DEBUG)
    log = logging.getLogger()
    
    def __init__(self, pie_find, path_list):
        self.pie_find = pie_find
        self.items = []
        for path in path_list:
            self.items.append(urwid.Text(path))
        
        content = urwid.SimpleListWalker([
                urwid.AttrMap(w, None, 'reveal focus') for w in self.items])
        
        self.listbox = urwid.ListBox(content)
        
        self.header_text = urwid.Text("Press any key", wrap='clip')
        footer_text = urwid.Text("", wrap='clip')
        footer_text.set_text("[o]pen, [d]iff, [q]uit")
        
        head = urwid.AttrMap(self.header_text, 'header')
        foot = urwid.AttrMap(footer_text, 'footer')
        top = urwid.Frame(self.listbox, head, foot)
        
        palette = [
            ('header', 'white', 'black'),
            ('footer', 'white', 'dark green'),
            ('reveal focus', 'black', 'dark cyan', 'standout')]
        
        self.loop = urwid.MainLoop(
            top, palette,
            input_filter=self.input_handler)

    def get_focus_index(self):
        focus_widget, idx = self.listbox.get_focus()
        return idx

    def get_focus_path(self):
        idx = self.get_focus_index()
        path, attrs = self.items[idx].get_text()
        return path

    def scroll_up(self, offset):
        idx = self.get_focus_index()
        if idx - offset > 0:
            idx = idx - offset
            self.listbox.set_focus(idx)
        else:
            self.scroll_to_first()

    def scroll_down(self, offset):
        idx = self.get_focus_index()
        if idx + offset > 0:
            idx = idx + offset
            self.listbox.set_focus(idx)
        else:
            self.scroll_to_last()

    def scroll_to_first(self):
        self.listbox.set_focus(0)

    def scroll_to_last(self):
        self.listbox.set_focus(len(self.items)-1)

    def input_handler(self, input, raw):
        key = " ".join([unicode(i) for i in input])
        self.header_text.set_text("Pressed: " + key)
        
        if key == 'down':
            self.scroll_down(1)
        elif key == 'up':
            self.scroll_up(1)
        elif key == 'page up':
            self.scroll_up(self.PAGE_SCROLL_SIZE)
        elif key == 'page down':
            self.scroll_down(self.PAGE_SCROLL_SIZE)
        elif key == 'home':
            self.scroll_to_first()
        elif key == 'end':
            self.scroll_to_last()
        elif key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif self.pie_find.has_key_mapping(key):
            cmd = self.pie_find.get_command(key)
            cmd = cmd.replace('$file', self.get_focus_path())
            self.log.debug(':: key ' + key + ' -> ' + cmd)
            CommandLineAction().execute(cmd)

    def start(self):
        self.loop.run()


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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('searchstring')
    parser.add_argument('basedir', nargs='?')
    return parser.parse_args()

args = parse_args()
basedir = os.curdir
if args.basedir is not None:
    basedir = args.basedir

config = PieConfig()


pie_find = PieFind(config)
path_list = sorted(pie_find.find_files(basedir, args.searchstring)) #XXX: refactor

ui = PieUI(pie_find, path_list)
ui.start()
