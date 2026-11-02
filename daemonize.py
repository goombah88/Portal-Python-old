#!/usr/bin/env python

# User modules
import settings
#
import os
import sys
import time
from threading import Thread
from Queue import Queue
import gobject
import gtk
gtk.gdk.threads_init()

# Load the file into a list

#string = raw_input('String: ')
string = sys.argv[1]
f = open('%s' % settings.ssh_config_file, 'r')
servers = list()
for line in f:
    line = line.strip()
    sline = line.split()
    if string in sline[1]:
        servers.append(sline[1])
servers = sorted(servers)
f.close()

COLUMN_TEXT = 0

class Daemonize:
    def __init__(self):
        self.multiple = "no"
        self.term_size = settings.term_size
        self.password = settings.password
        self.rh_exp = settings.rh_exp
        
        self.window = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(350, 400)
        self.window.set_position(gtk.WIN_POS_CENTER)
        
        self.window.connect("destroy", gtk.main_quit)
        self.window.connect("key-press-event", self.escape)
        self.window.set_title("Server Names")

        vbox = gtk.VBox(False, 8)
        
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        vbox.pack_start(sw, True, True, 0)

        button = gtk.Button("Launch Multiple")
        button.show()
        button.connect("clicked", self.multiple_clicked)
        vbox.pack_end(button, False, False, 0)

        store = self.create_model()

        self.treeview = gtk.TreeView(store)
        self.treeview.connect("row-activated", self.on_activated)
        self.treeview.set_rules_hint(True)
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        sw.add(self.treeview)

        self.create_columns(self.treeview)
        self.statusbar = gtk.Statusbar()
        
        vbox.pack_start(self.statusbar, False, False, 0)

        self.window.add(vbox)
        self.window.show_all()

    def escape(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()

    def create_model(self):
        store = gtk.ListStore(str)

        for act in servers:
            store.append([act])
        return store

    def create_columns(self, treeview):
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Server Name", rendererText, text=0)
        column.set_sort_column_id(0)    
        self.treeview.append_column(column)
        
    def foreach(self, model, path, iter, selected):
        self.selected.append(model.get_value(iter, COLUMN_TEXT))

    def multiple_clicked(self, event):
        self.window.set_skip_taskbar_hint(True)
        self.window.iconify()
        Thread(target=lambda : self.launch_multiple(event)).start()

    def launch_multiple(self, event):
        self.multiple = "yes"
        self.selected = []
        self.treeview.get_selection().selected_foreach(self.foreach, self.selected)
        #sys.exit(0)
        for server in self.selected:
            cmd = "rh %s" % server
            self.daemonize('gnome-terminal ', self.term_size, '--disable-factory', '-x', self.rh_exp, self.password, cmd)
            time.sleep(1)
        os._exit(0)

    def on_activated(self, widget, row, col):
        model = widget.get_model()
        self.text = model[row][0]
        self.server = self.text
        cmd = "rh %s" % self.server
        self.daemonize('gnome-terminal ', self.term_size, '--disable-factory', '-x', self.rh_exp, self.password, cmd)

    def daemonize(self, *args):
        #os.system("gnome-terminal --disable-factory -x /home/e65791/Desktop/rh.exp " + '"' + cmd + '"')
        try:
            pid = os.fork()
        except OSError, e:
            raise Exception, "%s [%d]" % (e.strerror, e.errno)
        if pid != 0:
            os._exit(0)
        else:
            os.setsid()
            try:
                pid = os.fork()
            except OSError, e:
                raise Exception, "%s [%d]" % (e.strerror, e.errno)
            if self.multiple == "no":
                if (pid == 0):
                    os.umask(0)
                    os.execv('/usr/bin/gnome-terminal', args)
                else:
                    os._exit(0)
            else:
                if (pid == 0):
                    os.umask(0)
                    os.execv('/usr/bin/gnome-terminal', args)

Daemonize()
gtk.gdk.threads_init()
gtk.main()
