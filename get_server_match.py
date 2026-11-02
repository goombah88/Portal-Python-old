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
f = open('/home/e65791/.ssh/config', 'r')
servers = list()
for line in f:
    line = line.strip()
    sline = line.split()
    if string in sline[1]:
        servers.append(sline[1])
f.close()

COLUMN_TEXT = 0

class Match: 
    def __init__(self):
        self.term_size = settings.term_size
        
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

        button = gtk.Button("Select Multiple")
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

        for srv in servers:
            store.append([srv])
        return store

    def create_columns(self, treeview):
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Server Name", rendererText, text=0)
        column.set_sort_column_id(0)    
        self.treeview.append_column(column)
        
    def foreach(self, model, path, iter, selected):
        self.selected.append(model.get_value(iter, COLUMN_TEXT))

    def multiple_clicked(self, event):
        self.selected = []
        self.treeview.get_selection().selected_foreach(self.foreach, self.selected)
        #sys.exit(0)
        for server in self.selected:
            print '%s' % server
        #os._exit(0)
        gtk.main_quit()

    def on_activated(self, widget, row, col):
        model = widget.get_model()
        self.server = model[row][0]
        print self.server
        gtk.main_quit()

Match()
gtk.gdk.threads_init()
gtk.main()
