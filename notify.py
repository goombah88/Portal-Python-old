#!/usr/bin/env python

# User modules
import settings
from popups import Popups
#
import csv
import smtplib
from email import MIMEText
import os
import sys
import time
import subprocess as sub
from threading import Thread
from Queue import Queue
import gobject
import gtk
gtk.gdk.threads_init()

class Notify:
    def escape(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()

    def __init__(self):
        #self.server = sys.argv[1]
        self.path = sys.path[0]
        self.notify_file = settings.notify_file
        self.email_address = settings.email_address
        self.name = settings.name
        self.last_name = self.name.split(',')[0]
        self.first_name = self.name.split(',')[1]

        self.window = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(350, 300)
        self.window.set_position(gtk.WIN_POS_CENTER)
        
        self.window.connect("destroy", gtk.main_quit)
        self.window.connect("key-press-event", self.escape)
        self.window.set_title("Send email for which fs?")

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        store = self.create_model()

        self.treeview = gtk.TreeView(store)
        self.treeview.connect("row-activated", self.on_activated)
        self.treeview.set_rules_hint(True)
        sw.add(self.treeview)

        self.create_columns(self.treeview)
        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0, 'To begin, search for a string')
        
        vbox = gtk.VBox(False, 8)

        hbox = gtk.HBox(False, 0)
        self.txtSearch = gtk.Entry(0)
        self.txtSearch.set_activates_default(True)
        btnSearch = gtk.Button('Search')
        btnSearch.connect("clicked", self.search_clicked, store)
        btnSearch.set_flags(gtk.CAN_DEFAULT)
        btnManage = gtk.Button('Manage File')
        btnManage.connect("clicked", self.manage_notify_file)
        hbox.pack_start(self.txtSearch, False, False, 0)
        hbox.pack_start(btnSearch, False, False, 0)
        hbox.pack_start(btnManage, False, False, 0)
        vbox.pack_start(hbox, False, False, 10)
        
        # Add the percent box
        hbox = gtk.HBox(False, 0)
        label = gtk.Label("What percent full is the filesystem?")
        label2 = gtk.Label("%")
        adjustment = gtk.Adjustment(2, 1, 100, 1, 1)
        self.percent = gtk.SpinButton(adjustment, 1, 0)
        self.percent.set_value(90.0)
        self.percent.set_numeric(True)
        self.percent.set_update_policy(gtk.UPDATE_IF_VALID)
        hbox.pack_start(label, True, True, 0)
        hbox.pack_end(label2, False, False, 0)
        hbox.pack_end(self.percent, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        vbox.pack_start(sw, True, True, 0)

        vbox.pack_start(self.statusbar, False, False, 0)

        self.window.add(vbox)
        self.window.set_default(btnSearch)
        self.window.show_all()

    def construct_to_field(self, CONTACTS):
        TO = list()
        # GROUPS
        if CONTACTS == 'DBAS':
            CONTACTS = 'ivo.bilikha;rajendra.govindaswamy;jining.han;kris.hanggi;<EMAIL>;suresh.ponnian;kevin.shidler;george.wang'
        for email in CONTACTS.split(';'):
            if '@' not in email:
                TO.append('%<EMAIL>' % email)
            else:
                TO.append(email)
        return TO

    def sendmail(self, SERVER_NAME, FS, CONTACTS, PERCENT):
        #PERCENT = 90
        SERVER = "localhost"

        FROM = self.email_address
        # TO must be a list
        TO = self.construct_to_field(CONTACTS)
        #sys.exit(0)
        #TO = ['<EMAIL>', '<EMAIL>']
        #TO = ['<EMAIL>']
        
        SUBJECT = "Please clean %s on %s"  % (FS, SERVER_NAME)
        
        body = """Please clean up %s on %s before the filesystem gets too full.\n\n%s is currently at %s%%.\n\nThanks,\n%s""" % \
                (FS, SERVER_NAME, FS, PERCENT, self.first_name)
        
        # Prepare actual message
        
        msg = MIMEText.MIMEText(body)
        #msg['From'] = 'Chad Crider <<EMAIL>>'
        msg['From'] = '%s %s <%s>' % \
                (self.first_name, self.last_name, self.email_address)
        msg['To'] = ",".join(TO)
        #msg['CC'] = 'Chad Crider <<EMAIL>>'
        msg['Subject'] = SUBJECT
        
        # Send the mail
        
        server = smtplib.SMTP(SERVER)
        #server.set_debuglevel(3)
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()
        #gtk.main_quit()

    def create_model(self):
        store = gtk.ListStore(str, str, str)

        #for srv in servers:
        #    store.append([srv])
        return store

    def create_columns(self, treeview):
        # Create Columns
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Server Name", rendererText, text=0)
        column.set_sort_column_id(0)    
        self.treeview.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Filesystem", rendererText, text=1)
        column.set_sort_column_id(1)    
        self.treeview.append_column(column)
        
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Contacts", rendererText, text=2)
        column.set_sort_column_id(2)    
        self.treeview.append_column(column)

    def on_activated(self, widget, row, col):
        model = widget.get_model()
        server_name = model[row][0]
        fs = model[row][1]
        contacts = model[row][2]
        PERCENT = str(self.percent.get_value()).split('.')[0]
        self.sendmail(server_name, fs, contacts, PERCENT)
        self.statusbar.push(0, 'Email sent for %s' % server_name)

    def search_clicked(self, w, store):
        store.clear()
        self.search_string = self.txtSearch.get_text()
        found = 0
        print 'searching for', self.search_string
        
        f = open(self.notify_file, 'rb')
        reader = csv.reader(f)
        for row in reader:
            if self.search_string in row[0]:
                found = 1
                server_name = row[0]
                fs = row[1]
                contacts = row[2]
                store.append([server_name, fs, contacts])
                #print "server - %s\nadding:\nserver - %s\nfs - %s\ncontacts - %s" % (self.server, server_name, fs, contacts)
        f.close()
        self.statusbar.push(0, 'Double-click result to send email')
        if found == 0:
            self.statusbar.push(0, 'No match found')

    def manage_notify_file(self, w):
        pop = Popups(self.window, '')
        popup = pop.manage_notify_file()

if __name__ == "__main__":
    notify = Notify()
    gtk.gdk.threads_init()
    gtk.main()
