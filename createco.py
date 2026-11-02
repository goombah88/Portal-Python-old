#!/usr/bin/env python

# User modules
import settings
#
import time
import os
import sys
import platform
import subprocess as sub
from threading import Thread
import gobject
import gtk
gtk.gdk.threads_init()

class CreateCO: 
    def __init__(self):
        # Set some variables
        self.term_size = settings.term_size
        self.terminal_cmd = settings.terminal_cmd
        self.portal_location = settings.portal_location
        self.gs_cmd_exp = settings.gs_cmd_exp
        self.sop_location = settings.sop_location
        self.fetch_all_exp = settings.fetch_all_exp
        self.fetch_one_exp = settings.fetch_one_exp
        self.get_sop_folder_list_exp = settings.get_sop_folder_list_exp
        self.push_sop_exp = settings.push_sop_exp
        self.sop_server_file = settings.sop_server_file
        self.hostname = settings.hostname
        self.co_wiz_script = settings.co_wiz_script
        self.launch_co_wiz_exp = settings.launch_co_wiz_exp

        if not os.path.exists(self.sop_location):
            os.mkdir(self.sop_location)

        # Get password from config file
        self.password = settings.password

        self.window = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(610, 800)
        self.window.set_position(gtk.WIN_POS_CENTER)
        
        self.window.connect("destroy", gtk.main_quit)
        self.window.connect("key-press-event", self.escape)
        self.window.set_title("Change Order Editor")

        #
        # Layout
        #

        MainVBox = gtk.VBox(False, 0)
        TopVBox = gtk.VBox(False, 0)
        TopVBox.set_size_request(-1, 125)
        ButtonHBox = gtk.HBox(False, 0)
        ContentVBox = gtk.VBox(False, 0)
        
        #
        # Top
        #

        # Combo box
        # Fetch the list of folders from opsware
        folder_list = self.fetch_folder_list()
        self.comboChoices = gtk.combo_box_new_text()
        self.comboChoices.set_size_request(200, -1)
        self.comboChoices.append_text("Choose the SOP to edit")
        for folder in folder_list:
            self.comboChoices.append_text(folder)
        self.comboChoices.set_active(0)
        TopVBox.pack_start(self.comboChoices, False, False, 0)
        
        btnLoadSOP = gtk.Button("Load SOP")
        btnLoadSOP.connect("clicked", self.launcher, 'load')
        ButtonHBox.pack_start(btnLoadSOP, False, False, 0)
        btnFetchSOP = gtk.Button("Fetch SOP")
        btnFetchSOP.connect("clicked", self.launcher, 'fetch_one')
        ButtonHBox.pack_start(btnFetchSOP, False, False, 0)
        btnFetchAllSOP = gtk.Button("Fetch All SOPs")
        btnFetchAllSOP.connect("clicked", self.launcher, 'fetch_all')
        ButtonHBox.pack_start(btnFetchAllSOP, False, False, 0)
        btnSaveSOP = gtk.Button("Save Changes")
        btnSaveSOP.connect("clicked", self.save_sop_clicked)
        ButtonHBox.pack_start(btnSaveSOP, False, False, 0)
        btnPushSOP = gtk.Button("Push Changes to GS")
        btnPushSOP.connect("clicked", self.launcher, 'push')
        ButtonHBox.pack_start(btnPushSOP, False, False, 0)
        btnLaunchWiz = gtk.Button("Launch Wizard")
        btnLaunchWiz.connect("clicked", self.launcher, 'wizard')
        ButtonHBox.pack_start(btnLaunchWiz, False, False, 0)

        TopVBox.pack_start(ButtonHBox, False, False, 10)

        # Server list
        hbox = gtk.HBox(False, 0)
        vbox1 = gtk.VBox(False, 0)
        label = gtk.Label("Server list (separated names with a space):")
        label.set_alignment(0, .5)
        self.txtSOPServerList = gtk.Entry(0)
        vbox1.pack_start(label, False, False, 0)
        vbox1.pack_start(self.txtSOPServerList, False, False, 0)
        hbox.pack_start(vbox1, True, True, 0)

        vbox2 = gtk.VBox(False, 0)
        label = gtk.Label("Remote .lst file to use")
        label.set_alignment(0, .5)
        self.txtSOPFile = gtk.Entry(0)
        self.txtSOPFile.set_text(self.sop_server_file)
        vbox2.pack_start(label, False, False, 0)
        vbox2.pack_start(self.txtSOPFile, False, False, 0)
        hbox.pack_end(vbox2, False, False, 10)

        TopVBox.pack_end(hbox, False, False, 0)


        MainVBox.pack_start(TopVBox, False, False, 10)

        #
        # Content
        #
        # Back, Desc, Impl, Val
        

        label = gtk.Label("<b>Description</b>")
        label.set_use_markup(True)
        label.set_alignment(0, .5)
        sw = gtk.ScrolledWindow()
        sw.set_size_request(-1, 150)
        self.TextDesc = gtk.TextView()
        #iter = self.TextDesc.get_buffer().get_iter_at_mark(self.TextDesc.get_buffer().get_insert())
        #self.TextDesc.get_buffer().insert(iter, "Description")
        sw.add(self.TextDesc)
        ContentVBox.pack_start(label, False, False, 0)
        ContentVBox.pack_start(sw, False, False, 0)

        label = gtk.Label("<b>Implementation Plan</b>")
        label.set_use_markup(True)
        label.set_alignment(0, .5)
        sw = gtk.ScrolledWindow()
        self.TextImpl = gtk.TextView()
        sw.add(self.TextImpl)
        ContentVBox.pack_start(label, False, False, 0)
        ContentVBox.pack_start(sw, True, True, 0)

        label = gtk.Label("<b>Backout Plan</b>")
        label.set_use_markup(True)
        label.set_alignment(0, .5)
        sw = gtk.ScrolledWindow()
        self.TextBack = gtk.TextView()
        sw.add(self.TextBack)
        ContentVBox.pack_start(label, False, False, 0)
        ContentVBox.pack_start(sw, False, False, 0)
        
        label = gtk.Label("<b>Validation Plan</b>")
        label.set_use_markup(True)
        label.set_alignment(0, .5)
        sw = gtk.ScrolledWindow()
        self.TextVal = gtk.TextView()
        sw.add(self.TextVal)
        ContentVBox.pack_start(label, False, False, 0)
        ContentVBox.pack_start(sw, False, False, 0)

        MainVBox.pack_start(ContentVBox, True, True, 0)

        # Progressbar
        self.progress = gtk.ProgressBar()
        MainVBox.pack_end(self.progress, False, False, 0)


        self.window.add(MainVBox)
        self.window.show_all()

    def fetch_all_sop_clicked(self):
        gobject.idle_add(self.progress.set_text, \
                'Copying down all SOPs from GlobalShell')
        process = sub.Popen('%s %s %s %s' %  \
                (self.fetch_all_exp, self.password, self.hostname, self.sop_location),\
                stdout=sub.PIPE, shell=True)
        process.wait()
        gobject.idle_add(self.progress.set_text, '-=/ Done \=-')

    def fetch_one_sop_clicked(self):
        active = self.comboChoices.get_active_text()
        activeSOP = '%s/%s/%s' % (self.sop_location, active, active)
        gobject.idle_add(self.progress.set_text, 'Fetching %s ...' % active)
        # Copy it down
        process = sub.Popen('%s %s %s %s %s' % \
                (self.fetch_one_exp, self.password, active, \
                self.hostname, self.sop_location), stdout=sub.PIPE, shell=True)
        process.wait()
        gobject.idle_add(self.progress.set_text, '-=/ Done \=-')
                
    def fetch_folder_list(self):
        folder_list = list()
        raw_output = sub.Popen('%s %s' % \
                (self.get_sop_folder_list_exp, self.password),\
                stdout=sub.PIPE, shell=True).communicate()[0]
        lss = raw_output.replace('\r', '')
        result = lss[lss.find("SOP")+4:lss.find("END")].split("\n")
        #folder_list = result[:-1]
        for item in result:
            if 'SOP/' in item:
                folder_list.append(os.path.split(item)[1])
        folder_list = sorted(folder_list, key=str.lower)
        return folder_list

    def save_sop_clicked(self, widget):
        active = self.comboChoices.get_active_text()
        activeSOP = '%s/%s/%s' % (self.sop_location, active, active)

        Desc = self.TextDesc.get_buffer().get_text\
                (*self.TextDesc.get_buffer().get_bounds())
        Impl = self.TextImpl.get_buffer().get_text\
                (*self.TextImpl.get_buffer().get_bounds())
        Back = self.TextBack.get_buffer().get_text\
                (*self.TextBack.get_buffer().get_bounds())
        Val = self.TextVal.get_buffer().get_text\
                (*self.TextVal.get_buffer().get_bounds())

        # Save the textviews to file
        f = open('%s.Desc' % activeSOP, 'w')
        f.write(Desc)
        f.close()
        f = open('%s.Back' % activeSOP, 'w')
        f.write(Back)
        f.close()
        f = open('%s.Impl' % activeSOP, 'w')
        f.write(Impl)
        f.close()
        f = open('%s.Val' % activeSOP, 'w')
        f.write(Val)
        f.close()

        # Save the server list
        f = open('%s.serverlist' % activeSOP, 'w')
        for server in self.txtSOPServerList.get_text().split(' '):
            f.write(server + '\n')
        f.close()

        self.progress.set_text('%s Saved' % active)

    def push_sop(self):
        active = self.comboChoices.get_active_text()
        activeSOP = '%s/%s/%s' % (self.sop_location, active, active)

        # Save the SOP first
        self.save_sop_clicked(self)
        gobject.idle_add(self.progress.set_text, \
                '%s Saved, now pushing to GlobalShell' % active)

        # Push SOP and SOP server '.lst' file
        command = '%s %s %s %s %s %s' % \
                (self.push_sop_exp, self.password, self.hostname, active, \
                self.sop_location, self.sop_server_file)
        process = sub.Popen(command, stdout=sub.PIPE, shell=True)
        process.wait()
        gobject.idle_add(self.progress.set_text, '%s Pushed' % active)

    def load_sop_clicked(self):
        #print self.TextDesc.get_buffer().get_text(*self.TextDesc.get_buffer().get_bounds())
        #self.TextDesc.get_buffer().set_text("TEST")
        active = self.comboChoices.get_active_text()
        activeSOP = '%s/%s/%s' % (self.sop_location, active, active)

        # If the SOP folder doesn't exist locally, copy it down first
        if not os.path.isdir('%s/%s' % (self.sop_location, active)):
            gobject.idle_add(self.progress.set_text, \
                    '%s not local, fetching...' % active)
            # Copy it down
            process = sub.Popen('%s %s %s' % \
                    (self.fetch_one_exp, self.password, active), \
                    stdout=sub.PIPE, shell=True)
            process.wait()
            gobject.idle_add(self.progress.set_text, '%s Loaded' % active)
        
        # Load the textviews
        self.TextDesc.get_buffer().set_text(open('%s.Desc' % activeSOP).read())
        self.TextImpl.get_buffer().set_text(open('%s.Impl' % activeSOP).read())
        self.TextBack.get_buffer().set_text(open('%s.Back' % activeSOP).read())
        self.TextVal.get_buffer().set_text(open('%s.Val' % activeSOP).read())

        # Load the server list
        f = open('%s.serverlist' % activeSOP)
        servers = f.read().replace('\n', ' ')
        self.txtSOPServerList.set_text(servers)
        f.close()

    def callback(self, widget, data=None):
        #print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
        pass

    def quit(self, widget, data=None):
        gtk.main_quit()

    def escape(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()

    def launcher(self, widget, action):
        if action == 'fetch_all':
            Thread(target=lambda : self.fetch_all_sop_clicked()).start()
        if action == 'load':
            Thread(target=lambda : self.load_sop_clicked()).start()
        if action == 'fetch_one':
            Thread(target=lambda : self.fetch_one_sop_clicked()).start()
        if action == 'push':
            Thread(target=lambda : self.push_sop()).start()
        if action == 'wizard':
            Thread(target=lambda : self.launch_wizard()).start()

    def submitCO(self):
        CO_Num = self.txtCO.get_text()
        activeMode = [r for r in self.radioStandard.get_group() if r.get_active()][0]
        activeCode = [r for r in self.radioSuccessful.get_group() if r.get_active()][0]
        mode = activeMode.get_label()
        code = activeCode.get_label()
        print 'CO:', CO_Num
        print 'active mode:', mode
        print 'active code:', code

        self.txtCO.modify_base(gtk.STATE_NORMAL, self.color_good)

        # Validate input
        if len(CO_Num) != 6:
            gobject.idle_add(self.progress.set_text, 'CO # wrong length')
            self.txtCO.modify_base(gtk.STATE_NORMAL, self.color_error)
        elif not CO_Num.isdigit():
            gobject.idle_add(self.progress.set_text, 'CO # not numeric')
            self.txtCO.modify_base(gtk.STATE_NORMAL, self.color_error)
        else:
            gobject.idle_add(self.progress.set_text, 'Executing...')
            if mode == 'Low':
                command = self.command_low
            elif mode == 'Standard':
                command = self.command_std
    
            cmd = "%s %s %s" % (command, CO_Num, code)
            print 'command is: ', cmd
            process = sub.Popen('gnome-terminal %s -x %s %s "%s"' % \
                    (self.term_size, self.gs_cmd_exp, self.password, cmd), \
                    shell=True, executable="/bin/bash")
            gobject.idle_add(self.progress.set_text, 'Done')
    
    def submitTask(self):
        activeMode = [r for r in self.radioComplete.get_group() if r.get_active()][0]
        mode = activeMode.get_label()
        TaskCO_Num = self.txtTaskCO.get_text()
        Task_Num = self.txtTaskNO.get_text()
        Task_Comment = self.txtTaskComment.get_text()
        print 'active mode:', mode
        print 'Task CO:', TaskCO_Num
        print 'Task #', Task_Num
        print 'Task Comment', Task_Comment

        self.txtTaskCO.modify_base(gtk.STATE_NORMAL, self.color_good)
        self.txtTaskNO.modify_base(gtk.STATE_NORMAL, self.color_good)

        for Task in Task_Num.split(','):
            # Validate input
            if len(TaskCO_Num) != 6:
                gobject.idle_add(self.progress.set_text, 'Task CO # wrong length')
                self.txtTaskCO.modify_base(gtk.STATE_NORMAL, self.color_error)
            elif not TaskCO_Num.isdigit():
                gobject.idle_add(self.progress.set_text, 'Task CO # not numeric')
                self.txtTaskCO.modify_base(gtk.STATE_NORMAL, self.color_error)
            elif not Task.isdigit():
                gobject.idle_add(self.progress.set_text, 'Task # not numeric')
                self.txtTaskNO.modify_base(gtk.STATE_NORMAL, self.color_error)
            elif Task == 'None' or Task == "":
                gobject.idle_add(self.progress.set_text, 'INVALID Task #')
                self.txtTaskNO.modify_base(gtk.STATE_NORMAL, self.color_error)
            else:
                gobject.idle_add(self.progress.set_text, 'Executing...')
                if mode == 'Complete':
                    command = self.command_task
                elif mode == 'Skip':
                    command = self.command_task_skip
                
                cmd = "%s %s %s '%s'" % (command, TaskCO_Num, Task, Task_Comment)
        
                print 'command is: ', cmd
                process = sub.Popen('gnome-terminal %s -x %s %s "%s"' % \
                        (self.term_size, self.gs_cmd_exp, self.password, cmd),\
                        shell=True, executable="/bin/bash")
                process.wait()
                gobject.idle_add(self.progress.set_text, 'Done')

    def launch_wizard(self):
        self.window.destroy()
        process = sub.Popen('%s %s %s %s' % \
                (self.terminal_cmd, self.launch_co_wiz_exp, \
                self.password, self.co_wiz_script), shell=True, executable="/bin/bash")
        process.wait()
        #gobject.idle_add(self.progress.set_text, 'Done')

create = CreateCO()
gtk.main()
