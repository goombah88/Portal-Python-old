#!/usr/bin/env python

# User modules
import settings
#
import time
import os
import sys
import subprocess as sub
from threading import Thread
import gobject
import gtk
gtk.gdk.threads_init()

class CompleteCO: 
    def __init__(self):
        # Set some variables
        self.term_size = settings.term_size
        self.portal_location = settings.portal_location
        self.gs_cmd_exp = settings.gs_cmd_exp
        self.command_low = settings.command_low
        self.command_std = settings.command_std
        self.command_task = settings.command_task
        self.command_task_skip = settings.command_task_skip
        self.color_error = settings.color_error
        self.color_good = settings.color_good

        # Get password from config file
        self.password = settings.password

        self.window = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(500, 275)
        self.window.set_position(gtk.WIN_POS_CENTER)
        
        self.window.connect("destroy", gtk.main_quit)
        self.window.connect("key-press-event", self.escape)
        self.window.set_title("Complete CO or Task")

        #
        # Layout
        #

        MainVBox = gtk.VBox(False, 0)
        ContentHBox = gtk.HBox(False, 0)

        # Left side
        COVBox = gtk.VBox(False, 0)
        COVBox.set_size_request(200, -1)
        ModeHBox = gtk.HBox(False, 0)
        CodeVBox = gtk.VBox(False, 0)

        # Right side
        TaskVBox = gtk.VBox(False, 0)
        TaskModeHBox = gtk.HBox(False, 0)
        TaskVBox.set_size_request(275, -1)
        ButtonHBox = gtk.HBox(False, 0)

        #
        # Content
        #
        
        # Radio buttons
        self.radioSuccessful = gtk.RadioButton(None, "Successful")
        self.radioSuccessful.connect("toggled", self.callback, "Successful")
        self.radioSuccessful.set_active(True)
        CodeVBox.pack_start(self.radioSuccessful, True, True, 0)
        
        self.radioAbandoned = gtk.RadioButton(self.radioSuccessful, "Abandoned")
        self.radioAbandoned.connect("toggled", self.callback, "Abandoned")
        self.radioAbandoned.set_active(False)
        CodeVBox.pack_start(self.radioAbandoned, True, True, 0)
        
        self.radioSuccessfulWInc = gtk.RadioButton(self.radioSuccessful, "SuccessfulWInc")
        self.radioSuccessfulWInc.connect("toggled", self.callback, "SuccessfulWInc")
        self.radioSuccessfulWInc.set_active(False)
        CodeVBox.pack_start(self.radioSuccessfulWInc, True, True, 0)
        
        # Mode Radio buttons
        self.radioStandard = gtk.RadioButton(None, "Standard")
        self.radioStandard.connect("toggled", self.callback, "Standard")
        self.radioStandard.set_active(True)
        ModeHBox.pack_start(self.radioStandard, True, True, 0)
        
        self.radioLow = gtk.RadioButton(self.radioStandard, "Low")
        self.radioLow.connect("toggled", self.callback, "Low")
        self.radioLow.set_active(False)
        ModeHBox.pack_start(self.radioLow, True, True, 0)

        #
        # CO side
        #

        # Header
        label = gtk.Label("<b><big><big>Complete COs</big></big></b>")
        label.set_use_markup(True)
        COVBox.pack_start(label, True, True, 10)

        hbox = gtk.HBox(False, 0)
        label = gtk.Label("CO #:")
        self.txtCO = gtk.Entry(0)
        self.txtCO.set_size_request(75, -1)
        self.txtCO.set_activates_default(True)
        hbox.pack_start(label, False, False, 0)
        hbox.pack_end(self.txtCO, False, False, 0)
        COVBox.pack_start(hbox, False, False, 0)

        COVBox.pack_start(ModeHBox, True, True, 0)

        separator = gtk.HSeparator()
        COVBox.pack_start(separator, False, True, 0)

        hbox = gtk.HBox(False, 0)
        self.txtStatus = gtk.Entry(0)
        self.txtStatus.set_activates_default(True)
        self.txtStatus.set_text("Successful")
        label = gtk.Label("Closure Code:")
        hbox.pack_start(label, False, False, 0)
        #hbox.pack_end(self.txtStatus, False, False, 0)
        COVBox.pack_start(hbox, True, True, 0)

        COVBox.pack_start(CodeVBox, False, False, 0)

        hbox = gtk.HBox(False, 0)
        self.btnSubmitCO = gtk.Button("Submit")
        self.btnSubmitCO.set_size_request(100, -1)
        self.btnSubmitCO.connect("clicked", self.launcher, 'CO')
        hbox.pack_end(self.btnSubmitCO, False, False, 0)
        COVBox.pack_end(hbox, False, False, 0)

        #
        # Task side
        #

        # Header
        label = gtk.Label("<b><big><big>Tasks</big></big></b>")
        label.set_use_markup(True)
        TaskVBox.pack_start(label, False, False, 10)

        # TaskMode Radio buttons
        self.radioComplete = gtk.RadioButton(None, "Complete")
        self.radioComplete.connect("toggled", self.callback, "Complete")
        self.radioComplete.set_active(True)
        TaskModeHBox.pack_start(self.radioComplete, True, True, 0)
        
        self.radioSkip = gtk.RadioButton(self.radioComplete, "Skip")
        self.radioSkip.connect("toggled", self.callback, "Skip")
        self.radioSkip.set_active(False)
        TaskModeHBox.pack_start(self.radioSkip, True, True, 0)

        TaskVBox.pack_start(TaskModeHBox, False, False, 0)

        hbox = gtk.HBox(False, 0)
        label = gtk.Label("CO #:                   ")
        self.txtTaskCO = gtk.Entry(0)
        self.txtTaskCO.set_size_request(75, -1)
        self.txtTaskCO.set_activates_default(True)
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(self.txtTaskCO, False, False, 0)
        TaskVBox.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox(False, 0)
        self.txtTaskNO = gtk.Entry(0)
        self.txtTaskNO.set_activates_default(True)
        self.txtTaskNO.set_size_request(50, -1)
        label = gtk.Label("Task Sequence #:")
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(self.txtTaskNO, False, False, 0)
        TaskVBox.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox(False, 0)
        self.txtTaskComment = gtk.Entry(0)
        self.txtTaskComment.set_activates_default(True)
        label = gtk.Label("Task Comment:    ")
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(self.txtTaskComment, False, False, 0)
        TaskVBox.pack_start(hbox, False, False, 0)

        ContentHBox.pack_start(COVBox, False, False, 0)
        separator = gtk.VSeparator()
        ContentHBox.pack_start(separator, False, True, 10)
        ContentHBox.pack_start(TaskVBox, False, False, 0)

        hbox = gtk.HBox(False, 0)
        self.btnSubmitTask = gtk.Button("Submit")
        self.btnSubmitTask.set_size_request(100, -1)
        self.btnSubmitTask.connect("clicked", self.launcher, 'Task')
        hbox.pack_end(self.btnSubmitTask, False, False, 0)
        TaskVBox.pack_end(hbox, False, False, 0)

        # Buttons
        btnCancel = gtk.Button("Cancel (ESC)")
        btnCancel.connect("clicked", self.quit)
        ButtonHBox.pack_end(btnCancel, False, False, 0)

        MainVBox.pack_start(ContentHBox, True, True, 0)

        # Progressbar
        self.progress = gtk.ProgressBar()
        MainVBox.pack_start(self.progress, True, True, 0)

        MainVBox.pack_end(ButtonHBox, False, False, 0)

        self.window.add(MainVBox)
        self.window.show_all()
        #self.window.set_default(btnSubmit)
        self.txtCO.grab_focus()

    def callback(self, widget, data=None):
        #print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
        pass

    def quit(self, widget, data=None):
        gtk.main_quit()

    def escape(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()

    def launcher(self, widget, action):
        if action == 'CO':
            Thread(target=lambda : self.submitCO()).start()
        if action == 'Task':
            Thread(target=lambda : self.submitTask()).start()

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
                
                print 'mode', mode
                print 'command', command
                cmd = "%s %s %s '%s'" % (command, TaskCO_Num, Task, Task_Comment)
        
                print 'command is: ', cmd
                process = sub.Popen('gnome-terminal %s -x %s %s "%s"' % \
                        (self.term_size, self.gs_cmd_exp, self.password, cmd),\
                        shell=True, executable="/bin/bash")
                process.wait()
                gobject.idle_add(self.progress.set_text, 'Done')

complete = CompleteCO()
gtk.main()
