#!/usr/bin/env python

# User modules
import settings
from popups import Popups
#
import os
import stat
import sys
import time
import subprocess as sub
from threading import Thread
from Queue import Queue
import gobject
import gtk
gtk.gdk.threads_init()

class Portal: 
    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def quit(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        self.term_size = settings.term_size
        self.silence_exp = settings.silence_exp
        
        # Get variables from config file
        self.password = settings.password
        self.term_size = settings.term_size
        self.portal_location = settings.portal_location
        self.gs_cmd_exp = settings.gs_cmd_exp
        self.command_low = settings.command_low
        self.command_std = settings.command_std
        self.command_task = settings.command_task
        self.command_task_skip = settings.command_task_skip
        self.color_error = settings.color_error
        self.color_good = settings.color_good
        self.name = settings.name
        self.terminal_cmd = settings.terminal_cmd
        self.ack_script = settings.ack_script
        self.close_script = settings.close_script
        self.ssh_config_file = settings.ssh_config_file
        self.translation_file = settings.translation_file
        self.rh_exp = settings.rh_exp
        self.gs_exp = settings.gs_exp
        self.daemonize_py = settings.daemonize_py
        self.silence_py = settings.silence_py
        self.get_server_match_py = settings.get_server_match_py
        self.get_servers_py = settings.get_servers_py
        self.ldap_server = settings.ldap_server
        self.ssh_server = settings.ssh_server
        self.completeco_py = settings.completeco_py
        self.createco_py = settings.createco_py
        self.notify_py = settings.notify_py
        self.mass_tickets_file = settings.mass_tickets_file
        self.fetch_mass_exp = settings.fetch_mass_exp
        self.notify_exp = settings.notify_exp
        self.listopentickets = settings.listopentickets_script
        self.hostname = settings.hostname
        self.default_method = settings.default_method
        self.fetch_reasons_exp = settings.fetch_reasons_exp
        self.notify_file = settings.notify_file
        self.reasons_file = settings.reasons_file

        # Get keywords from config file
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

        self.window = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(300, 100)
        self.window.set_position(gtk.WIN_POS_CENTER)
        
        self.window.connect("destroy", gtk.main_quit)
        self.window.connect("key-press-event", self.escape)
        self.window.set_title("Your wish is my command!")
        self.window.set_keep_above(True)

        vbox = gtk.VBox(False, 10)

        label = gtk.Label('Enter a keyword or help')
        label.set_use_markup(True)
        vbox.pack_start(label, False, False, 0)

        hbox = gtk.HBox(False, 0)
        self.txtEntry = gtk.Entry(0)
        self.txtEntry.set_size_request(150, -1)
        self.txtEntry.set_activates_default(True)
        hbox.pack_start(self.txtEntry, False, False, 75)
        vbox.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox(False, 0)
        btnExecute = gtk.Button(stock='gtk-execute')
        btnExecute.connect("clicked", self.execute_clicked)
        btnExecute.set_size_request(100, -1)
        btnExecute.set_flags(gtk.CAN_DEFAULT)
        hbox.pack_start(btnExecute, False, False, 100)
        vbox.pack_start(hbox, False, False, 0)
        
        self.window.add(vbox)
        self.window.show_all()
        self.window.set_default(btnExecute)

        sub.Popen("touch %s" % self.notify_file, shell=True, executable="/bin/bash")
        sub.Popen("touch %s" % self.reasons_file, shell=True, executable="/bin/bash")
        Thread(target=lambda : self.fetch_reasons()).start()

    def fetch_reasons(self):
        command = "%s %s %s %s" % \
            (self.fetch_reasons_exp, self.password, \
            self.hostname, self.portal_location)
        sub.Popen(command, shell=True, executable="/bin/bash")

    def escape(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()

    def ack_tickets(self, input):
        pop = Popups(self.window, '')
        #Thread(target=lambda : pop.ack()).start()
        tickets,impact,error = pop.ack(input)
        while error == 1:
            tickets,impact,error = pop.ack(input)
        #gtk.main_quit()
        cmd = ''
        for ticket in tickets.split(','):
            cmd = cmd + '%s %s %s -I %s; ' % \
                    (self.ack_script, ticket, self.name, impact)
        command = "%s %s %s '%s'" % \
            (self.terminal_cmd, self.gs_cmd_exp, self.password, cmd)
        returncode = sub.call(command, shell=True, executable="/bin/bash")
        if returncode == '249':
            #Repeat command
            sub.call(command, shell=True, executable="/bin/bash")

    def close_tickets(self, input):
        title = 'Close Ticket(s)'
        pop = Popups(self.window, title)
        tickets,impact,reason,error = pop.close_kill(input)
        while error == 1:
            tickets,impact,reason,error = pop.close_kill(input)

        #reason = self.check_auto_reason(reason)
        cmd = ''
        for ticket in tickets.split(','):
            cmd = cmd + '%s %s "%s"; ' % \
                    (self.close_script, ticket, reason)
        cmd = cmd.replace("'", "")
        print cmd
        command = "%s %s %s '%s'" % \
            (self.terminal_cmd, self.gs_cmd_exp, self.password, cmd)
        returncode = sub.call(command, shell=True, executable="/bin/bash")
        if returncode == '249':
            # Repeat command
            sub.call(command, shell=True, executable="/bin/bash")

    def ackclose_tickets(self, input):
        title = 'Kill Ticket(s)'
        pop = Popups(self.window, title)
        tickets,impact,reason,error = pop.close_kill(input)
        while error == 1:
            tickets,impact,reason,error = pop.close_kill(input)
        cmd = ''
        for ticket in tickets.split(','):
            cmd = cmd + '%s %s %s -I %s; %s %s "%s"; ' % \
                    (self.ack_script, ticket, self.name, impact, \
                    self.close_script, ticket, reason)
        cmd = cmd.replace("'", "")
        command = "%s %s %s '%s'" % \
            (self.terminal_cmd, self.gs_cmd_exp, self.password, cmd)
        returncode = sub.call(command, shell=True, executable="/bin/bash")
        if returncode == '249':
            # Repeat command
            sub.call(command, shell=True, executable="/bin/bash")

    def rosh(self, roshto):
        # Check the translations file first
        f = open(self.translation_file)
        match = 0
        for line in f:
            if line.strip().split()[0] == roshto:
                # Match
                match = 1
                server_name = line.strip().split()[1]
                break
        f.close()
        if match == 1:
            # Rosh to it
            command = '%s %s %s "rosh -l root -n %s"' % \
                    (self.terminal_cmd, self.rh_exp, self.password, server_name)
            process = sub.Popen(command, shell=True, executable="/bin/bash")
        else:
            # Now check the server list file
            string_count = open(self.ssh_config_file).read().count(roshto)
            if string_count == 1:
                # Found an EXACT match
                f = open(self.ssh_config_file)
                for line in f:
                    if roshto in line.strip().split()[1]:
                        host = line.strip().split()[1]
                        command = '%s %s %s "rosh -l root -n %s"' % \
                                (self.terminal_cmd, self.rh_exp, \
                                self.password, host)
                        process = sub.Popen(command, shell=True, \
                                executable="/bin/bash")
                        break
                f.close()
            elif string_count > 1:
                # No EXACT match found
                # show all matches
                process = sub.Popen('%s %s' % \
                        (self.daemonize_py, roshto), shell=True)
            else:
                # No match found
                dlg = Popups(self.window, '')
                dlg.no_match()
                gtk.main_quit()

    def ssh(self, sshto):
        if sshto:
            # Check the translations file first
            f = open(self.translation_file)
            match = 0
            for line in f:
                if line.strip().split()[0] == sshto:
                    # Match
                    match = 1
                    server_name = line.strip().split()[1]
                    break
            f.close()
            if match == 1:
                # SSH to it
                command = '%s ssh -o StrictHostKeyChecking=no %s' % \
                        (self.terminal_cmd, server_name)
                process = sub.Popen(command, shell=True, executable="/bin/bash")
            else:
                # Now check the server list file
                string_count = open(self.ssh_config_file).read().count(sshto)
                if string_count == 1:
                    # Found an EXACT match
                    f = open(self.ssh_config_file)
                    for line in f:
                        if sshto in line.strip().split()[1]:
                            host = line.strip().split()[1]
                            command = '%s ssh -o StrictHostKeyChecking=no %s' % \
                                    (self.terminal_cmd, host)
                            process = sub.Popen(command, shell=True, \
                                    executable="/bin/bash")
                            break
                    f.close()
                elif string_count > 1:
                    # No EXACT match found
                    # show all matches
                    process = sub.Popen('%s %s' % \
                            (self.daemonize_py, sshto), shell=True)
                else:
                    # No match found
                    dlg = Popups(self.window, '')
                    dlg.no_match()
                    gtk.main_quit()
        else:
            # No server given, so just SSH to the SSH server
            command = '%s ssh -o StrictHostKeyChecking=no %s' % \
                    (self.terminal_cmd, self.ssh_server)
            sub.Popen(command, shell=True, executable="/bin/bash")

    def execute_clicked(self, widget):
        self.string = self.txtEntry.get_text()
        self.window.destroy()

        # Check the string and act on it
        #
        # ACK
        #
        if self.string == self.keyword_ack:
            self.ack_tickets("")
        #
        # CLOSE
        #
        elif self.string == self.keyword_close:
            self.close_tickets("")
        #
        # ACKCLOSE
        #
        elif self.string == self.keyword_ackclose:
            self.ackclose_tickets("")
        elif self.string.startswith(self.keyword_rosh):
            roshto = self.string.split(self.keyword_rosh)[1]
            self.rosh(roshto)
        elif self.string.startswith(self.keyword_ssh):
            sshto = self.string.split(self.keyword_ssh)[1].strip()
            self.ssh(sshto)
        elif self.string == self.keyword_update:
                command = '%s %s %s' % (self.gs_cmd_exp, \
                        self.password, self.get_servers_py)
                sl = sub.Popen(command, stdout=sub.PIPE,shell=True).communicate()[0]
                serverlist = sl.split('\r\n')[7:-1]
                # Clean up the list a little
                serverlist = filter (lambda x: 'Cirrus' not in x, serverlist)
                serverlist = filter (lambda x: 'Template' not in x, serverlist)
                sorted(serverlist)
                if not os.path.exists(os.path.split(self.ssh_config_file)[0]):
                    os.makedirs(os.path.split(self.ssh_config_file)[0])
                    os.chmod(os.path.split(self.ssh_config_file)[0], 0o600)
                f = open(self.ssh_config_file, 'w')
                for item in serverlist:
                    f.write('Host %s\n' % item)
                f.close()
        elif self.string == self.keyword_gs:
            command = '%s %s %s' % \
                    (self.terminal_cmd, self.gs_exp, self.password)
            sub.Popen(command, shell=True, executable="/bin/bash")
        elif self.string == self.keyword_ldap:
            command = '%s ssh -o StrictHostKeyChecking=no %s' % \
                    (self.terminal_cmd, self.ldap_server)
            sub.Popen(command, shell=True, executable="/bin/bash")
        elif self.string == self.keyword_translation:
            title = 'Server Translations'
            pop = Popups(self.window, title)
            text = pop.translation()
        elif self.string == self.keyword_completeco:
            command = '%s' % self.completeco_py
            sub.Popen(command, shell=True, executable="/bin/bash")
        elif self.string == self.keyword_createco:
            command = '%s' % self.createco_py
            sub.Popen(command, shell=True, executable="/bin/bash")
        elif self.string == self.keyword_notify:
            Thread(target=lambda : self.pull_notify()).start()
            print 'done'
            sub.Popen(self.notify_py, shell=True, executable="/bin/bash")
        elif self.string == self.keyword_silence:
            sub.Popen(self.silence_py, shell=True, executable="/bin/bash")
        elif self.string == self.keyword_help:
            dlg = Popups(self.window, 'Portal Help')
            dlg.help()
        elif self.string == self.keyword_mass:
            # Fetch data
            command = "%s %s %s %s %s" % \
                (self.fetch_mass_exp, self.password, \
                self.hostname, self.portal_location, self.listopentickets)
            process = sub.Popen(command, shell=True, executable="/bin/bash")
            process.wait()

            dlg = Popups(self.window, '')
            action, tickets = dlg.mass_tickets()

            if action == 'ack':
                self.ack_tickets(tickets)
            if action == 'kill':
                self.ackclose_tickets(tickets)
        else:
            if self.default_method == 'rosh':
                print 'roshin it'
                self.rosh(self.string)
            elif self.default_method == 'ssh':
                print 'sshin it'
                self.ssh(self.string)
            else:
                # Invalid command
                dlg = Popups(self.window, '')
                dlg.no_match()
                gtk.main_quit()

    def pull_notify(self):
        command = "%s %s %s %s pull" % \
                (self.notify_exp, self.password, \
                self.hostname, self.portal_location)
        sub.Popen(command, shell=True, executable="/bin/bash")

        #################################################################
        #               TESTING
        #################################################################
    def check_auto_reason(self, reason):
        if reason.startswith('@'):
            keyword = reason.strip('@')
            if keyword == 'swap':
                new_reason = 'Temp spike in swap usage'
            if keyword == 'cpu':
                new_reason = 'Temp spike in CPU usage'
            if keyword == 'test':
                new_reason = 'Just testing a script'
            return new_reason
        #################################################################

if __name__ == "__main__":    
    portal = Portal()
    gtk.gdk.threads_init()
    gtk.main()
