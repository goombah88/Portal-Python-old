#!/usr/bin/env python

# User modules
import settings
#
import os
import sys
import time
import subprocess as sub
from threading import Thread
from Queue import Queue
import gobject
import gtk
gtk.gdk.threads_init()

COLUMN_TEXT = 0

class Silence: 
    def __init__(self):
        # Get variables from config file
        self.password = settings.password
        self.term_size = settings.term_size
        self.terminal_cmd = settings.terminal_cmd
        self.silence_exp = settings.silence_exp
        self.ssh_config_file = settings.ssh_config_file
        self.silence_script = settings.silence_script

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
        
        store = self.create_model()

        hbox = gtk.HBox(False, 0)
        self.txtSearch = gtk.Entry(0)
        self.txtSearch.connect("changed", self.search_clicked, store)
        self.txtSearch.set_activates_default(True)
        btnSearch = gtk.Button('Search')
        btnSearch.connect("clicked", self.search_clicked, store)
        btnSearch.set_flags(gtk.CAN_DEFAULT)
        hbox.pack_start(self.txtSearch, False, False, 0)
        hbox.pack_start(btnSearch, False, False, 0)
        vbox.pack_start(hbox, False, False, 10)

        button = gtk.Button("Choose Multiple")
        button.show()
        button.connect("clicked", self.multiple_clicked)
        
        vbox.pack_start(sw, True, True, 0)
        vbox.pack_end(button, False, False, 0)

        #if len(servers) == 1:
        #    # Exact match
        #    self.server = servers[0]
        #    self.multiple = "no"
        #    self.silence_options()


        self.treeview = gtk.TreeView(store)
        self.treeview.connect("row-activated", self.on_activated)
        self.treeview.set_rules_hint(True)
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        sw.add(self.treeview)

        self.create_columns(self.treeview)
        self.statusbar = gtk.Statusbar()
        
        vbox.pack_start(self.statusbar, False, False, 0)

        self.window.add(vbox)
        self.window.set_default(btnSearch)
        self.window.show_all()

    def escape(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()

    def create_model(self):
        store = gtk.ListStore(str)

        #for srv in servers:
        #    store.append([srv])
        return store

    def create_columns(self, treeview):
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Server Name", rendererText, text=0)
        column.set_sort_column_id(0)    
        self.treeview.append_column(column)
        
    def foreach(self, model, path, iter, selected):
        self.selected.append(model.get_value(iter, COLUMN_TEXT))

    def multiple_clicked(self, event):
        self.multiple = "yes"
        self.selected = []
        self.treeview.get_selection().selected_foreach(self.foreach, self.selected)
        self.silence_options()

    def on_activated(self, widget, row, col):
        self.multiple = "no"
        model = widget.get_model()
        self.server = model[row][0]
        self.silence_options()

    def silence_options(self):
        # Launch popup
        dialog = gtk.Dialog(
                "Silence Options",
                self.window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        dialog.set_size_request(300, 200)

        # Add the buttons
        btnOk = dialog.add_button(gtk.STOCK_OK, 1)
        btnCancel = dialog.add_button(gtk.STOCK_CANCEL, 0)

        # Content
        btnDefault = gtk.Button("1 hour for Reboot")
        btnDefault.connect("clicked", self.btnDefault_clicked)
        lblOr = gtk.Label("               - or -            ")
        CustomVBox = gtk.VBox(False, 0)
        HoursHBox = gtk.HBox(False, 0)
        CustomVBox.add(HoursHBox)

        lblNumHours = gtk.Label("# of hours to silence:")
        adjustment = gtk.Adjustment(2, 1, 192, 1, 1)
        self.numHours = gtk.SpinButton(adjustment, 1, 0)
        self.numHours.set_value(1.0)
        self.numHours.set_numeric(True)
        self.numHours.set_update_policy(gtk.UPDATE_IF_VALID)
        HoursHBox.pack_start(lblNumHours, True, True, 0)
        HoursHBox.pack_end(self.numHours, False, False, 0)

        # Reason
        lblReason = gtk.Label("Reason:")
        self.txtReason = gtk.Entry()
        self.txtReason.set_text("Reason for silencing server")
        self.txtReason.set_activates_default(True)
        CustomVBox.add(lblReason)
        CustomVBox.add(self.txtReason)

        dialog.set_default_response(1)
        dialog.vbox.pack_start(btnDefault, False, False, 0)
        dialog.vbox.pack_start(lblOr, True, True, 10)
        dialog.vbox.pack_start(CustomVBox, True, True, 10)
        dialog.show_all()
        response = dialog.run()
        if response == 0:
            #gtk.main_quit()
            dialog.destroy()
        elif response == 1:
            self.ok_clicked()
        dialog.destroy()

    def btnDefault_clicked(self, widget):
        # Assemble the command
        # Single server
        if self.multiple == "no":
            command = "%s %s now %d -r 'Reboot'" \
                    % (self.silence_script, self.server, self.numHours.get_value())
            returncode = sub.Popen('%s %s %s "%s"' % \
                    (self.terminal_cmd, self.silence_exp, self.password, \
                    command), shell=True, executable="/bin/bash")
                    #if returncode == '249':
                #Repeat command
                #sub.call(command, shell=True, executable="/bin/bash")
            sys.exit(0)

        # Multiple servers
        if self.multiple == "yes":
            command = ''
            for server in self.selected:
                command = "%s %s now %d -r Reboot" % \
                        (self.silence_script, server, self.numHours.get_value())
                #command += '%s; ' % cmd
                returncode = sub.Popen("%s %s %s '%s'" % \
                        (self.terminal_cmd, self.silence_exp, self.password, \
                        command), shell=True, executable="/bin/bash")
                        #if returncode == '249':
                    #Repeat command
                    #sub.call(command, shell=True, executable="/bin/bash")
            gtk.main_quit()

    def ok_clicked(self):
        # Assemble the command
        # Single server
        if self.multiple == "no":
            command = "%s %s now %d -r '%s'" \
                    % (self.silence_script, self.server, \
                    self.numHours.get_value(), \
                    self.txtReason.get_text())
            returncode = sub.Popen('%s %s %s "%s"' % \
                    (self.terminal_cmd, self.silence_exp, self.password, \
                    command), shell=True, executable="/bin/bash")
                    #if returncode == '249':
                #Repeat command
                #sub.call(command, shell=True, executable="/bin/bash")
            gtk.main_quit()

        # Multiple servers
        if self.multiple == "yes":
            command = ''
            for server in self.selected:
                command = "%s %s now %d -r '%s'" % \
                        (self.silence_script, server, \
                        self.numHours.get_value(), \
                        self.txtReason.get_text())
                returncode = sub.Popen('%s %s %s "%s"' % \
                        (self.terminal_cmd, self.silence_exp, self.password, \
                        command), shell=True, executable="/bin/bash")
                        #if returncode == '249':
                    #Repeat command
                    #sub.call(command, shell=True, executable="/bin/bash")
            gtk.main_quit()

    def search_clicked(self, w, store):
        store.clear()
        self.search_string = self.txtSearch.get_text()
        found = 0

        f = open(self.ssh_config_file, 'rb')
        for line in f:
            if self.search_string in line.split()[1]:
                found = 1
                server_name = line.split()[1]
                store.append([server_name])
        f.close()
        if found == 0:
            store.append(['no match'])

Silence()
gtk.gdk.threads_init()
gtk.main()
