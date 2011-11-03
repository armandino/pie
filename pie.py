import logging
import urwid
import subprocess

import argparse
import re
import os
from os.path import isfile
import sys


class PieUI(urwid.ListWalker):

    logging.basicConfig(filename='/tmp/pie.log', level=logging.DEBUG)
    log = logging.getLogger()
    
    def __init__(self, path_list):
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

    # these actions should be factored out of UI
    def open_file(self, path, **kwargs):
        editor_cmd = kwargs['editor']
        cmd = editor_cmd.split()
        cmd.append(path)
        self.log.debug(cmd)
        subprocess.call(cmd)
        
    def svn_diff(self, path, **kwargs):
        self.log.debug("svn diff " + path)
        subprocess.call("svn diff " + path + " | less", shell=True)

    def get_focus_index(self):
        focus_widget, idx = self.listbox.get_focus()
        return idx

    def get_focus_path(self):
        idx = self.get_focus_index()
        path, attrs = self.items[idx].get_text()
        return path

    def input_handler(self, input, raw):
        key = " ".join([unicode(i) for i in input])
        self.header_text.set_text("Pressed: " + key)
        
        if key == 'down':
            self.log.debug('down')
            idx = self.get_focus_index()
            self.log.debug('idx='+str(idx))
            
            if idx < len(self.items) - 1:
                idx = idx+1
                self.listbox.set_focus(idx)
        elif key == 'up':
            idx = self.get_focus_index()
            self.log.debug('idx='+str(idx))
            if idx > 0:
                idx = idx-1
                self.listbox.set_focus(idx)
                
        elif key in ('o', 'O'):
            path = self.get_focus_path()
            self.open_file(path, editor='emacs -nw')
        elif key in ('d', 'D'):
            path = self.get_focus_path()
            self.svn_diff(path)
        elif key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def start(self):
        self.loop.run()


class PieFind:
    EXCLUDED_DIRS=['.git', '.hg', 'target', 'bin', 'classes']

    def find_files(self, baseDir, searchstring, results=[]):
        try:
            dirList = os.listdir(baseDir)
        except OSError:
            dirList = []

        subDirs = []
        for item in dirList:
            path = os.path.join(baseDir, item)
            if isfile(path):
                if self.matches(searchstring, item):
                    if path.startswith('./'):
                        path = path[2:]
                    results.append(path)
            else:
                if item not in self.EXCLUDED_DIRS:
                    subDirs.append(path)

        for subDir in subDirs:
            self.find_files(subDir, searchstring, results)

        return results

    def matches(self, searchstring, item):
        return re.search(searchstring, item, re.IGNORECASE)



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('searchstring')
    parser.add_argument('basedir', nargs='?')
    return parser.parse_args()

args = parse_args()
basedir = os.curdir
if args.basedir is not None:
    basedir = args.basedir

pie_find = PieFind()
path_list = sorted(pie_find.find_files(basedir, args.searchstring))

ui = PieUI(path_list)
ui.start()