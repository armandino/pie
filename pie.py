#!/usr/bin/env python

import argparse
import logging
import os
import urwid

from pieconfig import PieConfig
from piecontrol import PieFind, CommandLineAction

# TODO: fix error - python pie.py /tmp/
# TODO: popup to allow executing an arbitrary command

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
        self.footer_text = urwid.Text("", wrap='clip')
        self.footer_text.set_text("Found %i files" % len(self.items))
        
        head = urwid.AttrMap(self.header_text, 'header')
        foot = urwid.AttrMap(self.footer_text, 'footer')
        top = urwid.Frame(body=self.listbox, header=head, footer=foot)
        
        palette = [
            ('header', 'white', 'black'),
            ('footer', 'white', 'dark green'),
            ('reveal focus', 'black', 'dark cyan', 'standout')]
        
        self.loop = urwid.MainLoop(
            widget=top,
			palette=palette,
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
            self.scroll_to(idx)
        else:
            self.scroll_to_first()

    def scroll_down(self, offset):
        idx = self.get_focus_index()
        if idx + offset < len(self.items):
            idx = idx + offset
            self.scroll_to(idx)
        else:
            self.scroll_to_last()

    def scroll_to_first(self):
        self.scroll_to(0)

    def scroll_to_last(self):
        self.scroll_to(len(self.items))

    def scroll_to(self, idx):
        self.listbox.set_focus(idx)
        self.footer_text.set_text("%i / %i" % (idx, len(self.items)))

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



def main():
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('searchstring')
        parser.add_argument('basedir', nargs='?')
        return parser.parse_args()

    args = parse_args()
    basedir = os.curdir
    if args.basedir is not None:
        basedir = args.basedir

    pie_find = PieFind(PieConfig())
    path_list = sorted(pie_find.find_files(basedir, args.searchstring)) #XXX: refactor

    if path_list:
        ui = PieUI(pie_find, path_list)
        ui.start()
    else:
        print "No files matching", args.searchstring

if __name__=="__main__": 
    main()
