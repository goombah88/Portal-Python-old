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

class Popups(object): 
    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def quit(self, widget, data=None):
        gtk.main_quit()

    def __init__(self, window, title):
        self.window = window
        self.title = title
        self.translation_file = settings.translation_file
        self.ldap_server = settings.ldap_server
        self.ssh_server = settings.ssh_server
        self.notify_file = settings.notify_file
        self.mass_tickets_file = settings.mass_tickets_file
        self.ack_script = settings.ack_script
        self.name = settings.name
        self.terminal_cmd = settings.terminal_cmd
        self.notify_exp = settings.notify_exp
        self.password = settings.password
        self.portal_location = settings.portal_location
        self.hostname = settings.hostname
        self.reasons_file = settings.reasons_file

        # Bring in keywords for help dialog
        self.keyword_help = settings.keyword_help
        self.keyword_ack = settings.keyword_ack
        self.keyword_close = settings.keyword_close
        self.keyword_ackclose = settings.keyword_ackclose
        self.keyword_translation = settings.keyword_translation
        self.keyword_rosh = settings.keyword_rosh
        self.keyword_gs = settings.keyword_gs
        self.keyword_silence = settings.keyword_silence
        self.keyword_update = settings.keyword_update
        self.keyword_ldap = settings.keyword_ldap
        self.keyword_ssh = settings.keyword_ssh
        self.keyword_faillog = settings.keyword_faillog
        self.keyword_notify = settings.keyword_notify
        self.keyword_completeco = settings.keyword_completeco
        self.keyword_createco = settings.keyword_createco
        self.keyword_mass = settings.keyword_mass

##############################################
#
# Various popups
#
##############################################

    def ack(self, input):
        # Launch popup
        dialog = gtk.Dialog(
                "Acknowledge Ticket(s)",
                self.window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        dialog.set_size_request(250, 125)
        dialog.set_keep_above(True)

        # Add the buttons
        btnOk = dialog.add_button(gtk.STOCK_EXECUTE, 1)
        btnCancel = dialog.add_button(gtk.STOCK_CANCEL, 0)

        # Content
        vbox = gtk.VBox(False, 0)

        hbox = gtk.HBox(False, 10)
        label = gtk.Label("Ticket #s?:")
        txtTickets = gtk.Entry()
        txtTickets.set_activates_default(True)
        if input:
            txtTickets.set_text(input)
        hbox.pack_start(label, False, False, 0)
        hbox.pack_end(txtTickets, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox(False, 10)
        label = gtk.Label("Impact?")

        adjustment = gtk.Adjustment(2, 1, 5, 1, 1)
        txtImpact = gtk.SpinButton(adjustment, 1, 0)
        txtImpact.set_value(float(5))
        txtImpact.set_numeric(True)
        txtImpact.set_update_policy(gtk.UPDATE_IF_VALID)
        txtImpact.set_activates_default(True)

        hbox.pack_start(label, False, False, 0)
        hbox.pack_end(txtImpact, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        dialog.vbox.pack_start(vbox, True, True, 10)
        dialog.set_default_response(1)
        dialog.show_all()
        response = dialog.run()

        if response == 0:
            gtk.main_quit()
        elif response == 1:
            error = 0
            if txtTickets.get_text() == "" or txtImpact.get_text() == "":
                error = 1
            return txtTickets.get_text(), txtImpact.get_text(), error
            dialog.destroy()
        dialog.destroy()

    def close_kill(self, input):
        # Launch popup
        dialog = gtk.Dialog(
                self.title,
                self.window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        dialog.set_size_request(250, 200)
        dialog.set_keep_above(True)

        # Add the buttons
        btnOk = dialog.add_button(gtk.STOCK_EXECUTE, 1)
        btnCancel = dialog.add_button(gtk.STOCK_CANCEL, 0)

        # Content
        vbox = gtk.VBox(False, 0)

        hbox = gtk.HBox(False, 10)
        label = gtk.Label("Ticket #s?:")
        txtTickets = gtk.Entry()
        txtTickets.set_activates_default(True)
        if input:
            txtTickets.set_text(input)
        hbox.pack_start(label, False, False, 0)
        hbox.pack_end(txtTickets, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        label = gtk.Label("Reason for closing?")
        label.set_alignment(0, .5)

        hbox = gtk.HBox(False, 10)
        self.txtReason = gtk.Entry()
        self.txtReason.set_activates_default(True)
        self.comboReasons = gtk.combo_box_new_text()
        self.comboReasons.connect("changed", self.changed_reason)
        self.comboReasons.set_size_request(25, -1)
        listReasons = list()
        for line in open(self.reasons_file).readlines():
            listReasons.append(line)
        listReasons = sorted(listReasons, key=str.lower)
        for item in listReasons:
            self.comboReasons.append_text(item)
        hbox.pack_start(self.txtReason, True, True, 0)
        hbox.pack_end(self.comboReasons, False, False, 0)

        vbox.pack_start(label, False, False, 10)
        vbox.pack_start(hbox, False, False, 0)
        
        hbox = gtk.HBox(False, 10)
        label = gtk.Label("Impact?")
        adjustment = gtk.Adjustment(2, 1, 5, 1, 1)
        txtImpact = gtk.SpinButton(adjustment, 1, 0)
        txtImpact.set_value(float(5))
        txtImpact.set_numeric(True)
        txtImpact.set_update_policy(gtk.UPDATE_IF_VALID)
        txtImpact.set_activates_default(True)

        hbox.pack_start(label, False, False, 0)
        hbox.pack_end(txtImpact, False, False, 0)
        if 'Kill' in self.title:
            vbox.pack_start(hbox, False, False, 0)


        dialog.vbox.pack_start(vbox, True, True, 10)
        dialog.set_default_response(1)
        dialog.show_all()
        response = dialog.run()

        if response == 0:
            gtk.main_quit()
        elif response == 1:
            error = 0
            if txtTickets.get_text() == "" or txtImpact.get_text() == "" or \
                    self.txtReason.get_text() == "":
                error = 1
            return txtTickets.get_text(), txtImpact.get_text(), \
                    self.txtReason.get_text(), error
        dialog.destroy()

    def changed_reason(self, w):
        new_reason = self.comboReasons.get_active_text().strip()
        self.txtReason.set_text(new_reason)

    def no_match(self):
        dlg = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, \
                gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, "No match found.")
        dlg.run()
        dlg.destroy()

    def translation(self):
        # Launch popup
        dialog = gtk.Dialog(
                self.title,
                self.window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        dialog.set_size_request(300, 350)
        dialog.set_keep_above(True)

        # Add the buttons
        btnSave = dialog.add_button(gtk.STOCK_SAVE, 1)
        btnCancel = dialog.add_button(gtk.STOCK_CANCEL, 0)

        # Content
        vbox = gtk.VBox(False, 0)

        #hbox = gtk.HBox(False, 10)
        label = gtk.Label("<b>Code\t\tServer Name</b>")
        label.set_alignment(0, .5)
        label.set_use_markup(True)
        sw = gtk.ScrolledWindow()
        self.textarea = gtk.TextView()
        sw.add(self.textarea)
        #sw.set_size_request(225, 150)
        self.textarea.set_editable(True)

        # Load the textview
        self.textarea.get_buffer().set_text(open(self.translation_file).read())

        vbox.pack_start(label, False, False, 0)
        vbox.pack_end(sw, True, True, 0)
        #vbox.pack_start(hbox, False, False, 0)

        dialog.vbox.pack_start(vbox, True, True, 10)
        dialog.set_default_response(1)
        dialog.show_all()
        response = dialog.run()

        if response == 0:
            gtk.main_quit()
        elif response == 1:
            text = self.textarea.get_buffer().get_text\
                    (*self.textarea.get_buffer().get_bounds())
            f = open(self.translation_file, 'w')
            f.write(text)
            f.close()
            return
        dialog.destroy()

    def help(self):
        # Launch popup
        dialog = gtk.Dialog(
                self.title,
                self.window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        dialog.set_size_request(415, 550)
        dialog.set_keep_above(True)

        # Add the buttons
        btnClose = dialog.add_button(gtk.STOCK_CLOSE, 0)

        # Content
        vbox = gtk.VBox(False, 0)
        text = """
Possible keywords/commands:\n\n\
<b>%s</b> - Acknowledge ticket(s)\n\
<b>%s</b> - Close ticket(s)\n\
<b>%s</b> - Ack and Close ticket(s)\n\
<b>%s</b> - update serverlist from globalshell\n\
<b>%s</b> - Completely silence a server for a given\n\t\tamount of time\n\
<b>%s</b> - ssh's you to %s\n\
<b>%s</b> - opens globalshell window\n\
<b>%s</b> - SSH's you to %s\n\
<b>%s \"server\"</b> - opens globalshell and rosh's you into\n\t\t\t a server as root\n\t\t     - checks the server translations file for\n\t\t\tmatches first\n\
<b>ssh \"server name\"</b> - ssh to the given server as yourself\n(can type partial names and it will list matches)\n\
<b>%s</b> - displays the server translations file for editing\n\
<b>%s</b> - Launch window to create/edit COs and push them\nto globalshell\n\
<b>%s</b> - Close COs, complete/skip CO tasks\n\
<b>%s</b> - Email people about filesystems which are getting too\nfull\n\
<b>%s</b> - Ack or Ack/Close all open tickets at once\n\
<b>%s</b> - this help screen""" % \
        (self.keyword_ack,
        self.keyword_close,
        self.keyword_ackclose,
        self.keyword_update,
        self.keyword_silence,
        self.keyword_ldap, self.ldap_server,
        self.keyword_gs,
        self.keyword_ssh, self.ssh_server,
        self.keyword_rosh,
        self.keyword_translation,
        self.keyword_createco,
        self.keyword_completeco,
        self.keyword_notify,
        self.keyword_mass,
        self.keyword_help)


        label = gtk.Label(text)
        label.set_use_markup(True)
        label.set_alignment(0, .5)
        vbox.pack_start(label, True, True, 5)

        dialog.set_default_response(0)
        dialog.vbox.pack_start(vbox, True, True, 10)
        dialog.show_all()
        response = dialog.run()

        if response == 0:
            gtk.main_quit()

    def manage_notify_file(self):
        # Launch popup
        dialog = gtk.Dialog(
                self.title,
                self.window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        dialog.set_size_request(600, 450)
        dialog.set_keep_above(True)

        # Add the buttons
        btnSave = dialog.add_button(gtk.STOCK_SAVE, 1)
        btnClose = dialog.add_button(gtk.STOCK_CLOSE, 0)

        # Content
        vbox = gtk.VBox(False, 0)

        label = gtk.Label("<b>Server\tFilesystem\tContacts</b>")
        label.set_alignment(0, .5)
        label.set_use_markup(True)
        vbox.pack_start(label, False, False, 0)
        sw = gtk.ScrolledWindow()
        self.textarea = gtk.TextView()
        sw.add(self.textarea)
        vbox.pack_start(sw, True, True, 0)
        #sw.set_size_request(225, 150)
        self.textarea.set_editable(True)

        # Load the textview
        self.textarea.get_buffer().set_text(open(self.notify_file).read())
        
        # Add entry
        label = gtk.Label("Add entry")
        vbox.pack_start(label, False, False, 0)
        label = gtk.Label("<b>Server\t\t\tFilesystem\t\tContacts</b>")
        label.set_alignment(0, .5)
        label.set_use_markup(True)
        vbox.pack_start(label, False, False, 0)
        AddHBox = gtk.HBox(False, 0)
        vbox.pack_start(AddHBox, False, False, 0)
        entryServer = gtk.Entry()
        entryFS = gtk.Entry()
        entryContacts = gtk.Entry()
        AddHBox.pack_start(entryServer, False, False, 0)
        AddHBox.pack_start(entryFS, False, False, 0)
        AddHBox.pack_start(entryContacts, True, True, 0)
        button = gtk.Button("Add")
        button.connect("clicked", self.add_entry, entryServer, entryFS, entryContacts)
        AddHBox.pack_start(button, False, False, 0)

        dialog.vbox.pack_start(vbox, True, True, 10)
        dialog.set_default_response(1)
        dialog.show_all()
        response = dialog.run()

        if response == 1:
            # Save changes to file
            text = self.textarea.get_buffer().get_text\
                    (*self.textarea.get_buffer().get_bounds())
            f = open(self.notify_file, 'w')
            f.write(text)
            f.close()
            # Push to GS
            command = "%s %s %s %s push" % \
                (self.notify_exp, self.password, \
                self.hostname, self.portal_location)
            sub.Popen(command, shell=True, executable="/bin/bash")

        dialog.destroy()

    def add_entry(self, widget, server, fs, contacts):
        text = '%s,%s,%s' % (server.get_text(), fs.get_text(), contacts.get_text())
        self.textarea.get_buffer().insert(self.textarea.get_buffer().get_end_iter(), "\n" + text)

    def mass_tickets(self):
        # Launch popup
        self.dlgMass = gtk.Dialog(
                "Manage Mass Tickets",
                self.window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        self.dlgMass.set_size_request(600, 450)
        self.dlgMass.set_keep_above(True)

        # Dialog buttons
        btnClose = self.dlgMass.add_button(gtk.STOCK_CLOSE, 0)

        # Content
        vbox = gtk.VBox(False, 0)

        sw = gtk.ScrolledWindow()
        vbox.pack_start(sw, True, True, 0)
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        store = gtk.ListStore(str, str, str, str)

        # Load the liststore
        if 'Number of tickets: 0' not in open(self.mass_tickets_file).read():
            for line in open(self.mass_tickets_file).readlines():
                if 'Number of tickets:' in line:
                    continue
                else:
                    ticket_num = line.split()[1].strip(':')
                    priority = line.split()[2]
                    impact = line.split()[3]
                    summary = line[line.find("Sum:")+4:]
                    store.append([ticket_num, priority, impact, summary])
        else:
            store.append(["", "", "", "No open tickets returned"])
        
        self.treeview = gtk.TreeView(store)
        self.treeview.connect("row-activated", self.on_activated)
        self.treeview.set_rules_hint(True)
        sw.add(self.treeview)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Ticket #", rendererText, text=0)
        column.set_sort_column_id(0)
        self.treeview.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Pri", rendererText, text=1)
        column.set_sort_column_id(1)
        self.treeview.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Imp", rendererText, text=2)
        column.set_sort_column_id(2)
        self.treeview.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Summary", rendererText, text=3)
        column.set_sort_column_id(3)
        self.treeview.append_column(column)

        # Buttons
        buttonHBox = gtk.HBox(True, 0)
        button = gtk.Button("Acknowledge All")
        button.connect("clicked", self.dump, 'ack')
        buttonHBox.pack_start(button, False, False, 50)
        button = gtk.Button("Ack & Close All")
        button.connect("clicked", self.dump, 'kill')
        buttonHBox.pack_start(button, False, False, 50)

        vbox.pack_start(buttonHBox, False, False, 0)

        self.statusbar = gtk.Statusbar()
        vbox.pack_end(self.statusbar, False, False, 0)

        self.dlgMass.vbox.pack_start(vbox, True, True, 10)
        self.dlgMass.set_default_response(1)
        self.dlgMass.show_all()
        response = self.dlgMass.run()

        if response == 0:
            gtk.main_quit()
        return self.action, self.tickets

    def on_activated(self, widget, row, col):
        model = widget.get_model()
        ticket_num = model[row][0]
        priority = model[row][1]
        summary = model[row][2]
        selection = widget.get_selection()
        result = selection.get_selected()
        if result:
            model, iter = result
        model.remove(iter)
        self.statusbar.push(0, 'Removed %s %s %s' % (ticket_num, priority, summary))

    def dump(self, widget, action):
        self.action = action

        print 'dumping'
        model = self.treeview.get_model()
        ticket_num = model[0]

        tickets = ""
        for ticket in model:
            tickets = tickets + ',' + ticket[0]

        self.tickets = tickets[1:]
        self.dlgMass.destroy()

if __name__ == "__main__":    
    popups = Popups()
    gtk.gdk.threads_init()
    gtk.main()
