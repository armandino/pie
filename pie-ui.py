import logging
import urwid
import subprocess


class UI(urwid.ListWalker):

    logging.basicConfig(filename='/tmp/pf.log', level=logging.DEBUG)
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

    #raw_input("Press Enter to continue...")
    def input_handler(self, input, raw):
        key = " ".join([unicode(i) for i in input])
        self.header_text.set_text("Pressed: " + key)
        #self.log.debug('handler: ' + key)
        
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

"""
path_list = [
    "/home/arman/Downloads/dinqy/pom.xml",
    "/home/arman/Downloads/dinqy/src/main/java/org/dinqy/Dinqy.java",
    "/home/arman/Downloads/dinqy/src/main/java/org/dinqy/JPQLSyntax.java"]
"""
path_list = []
for i in range(92):
    path_list.append('test'+str(i));

ui = UI(path_list)
ui.start()
