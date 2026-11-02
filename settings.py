#!/usr/bin/env python

import os
import platform
import gtk

#
# START CUSTOMIZE
#
# Your name as seen in ServiceDesk, in the format Last,First
name = 'Crider,Chad'
email_address = '<EMAIL>'
sop_server_file = "chad.lst"
###################################################################
# Set the portal_location
# Most important setting - many others get set off of this
#
portal_location = "/home/goombah/scripts/Dropbox/Portal-Python"
###################################################################
# Set your default connection method when typing a partial server
# name in the main portal window
# Can be either rosh or ssh
default_method = 'rosh'
###################################################################
# END CUSTOMIZE

#
# START STATIC
#
# Misc. settings
term_size = "--geometry=87x27"
hostname = platform.node().split('.')[0]
home = os.getenv('HOME')
ldap_server = 'punifirds010'
ssh_server = 'punifissh010'

###################################################################
# Set to True if you'd like to see terminal windows pop up
# for commands such as ack, close, silence, etc.
# If False, then commands will be launched in the background and not seen
use_terminal_window = True

if use_terminal_window:
    terminal_cmd = 'gnome-terminal %s --disable-factory -x ' % term_size
else:
    terminal_cmd = ''
###################################################################

###################################################################
# Set password to wherever you decide to hide the .portal.conf file
# which contains your password used by expect scripts to log you into 
# GlobalShell.
#
password = open('%s/.portal.conf' % portal_location).read().strip()
###################################################################

# Automatically set based on the portal_location
# Don't modify unless you REALLY know what you're doing
#
silence_exp = "%s/silence.exp" % portal_location
fetch_all_exp = "%s/fetch_all_sops.exp" % portal_location
fetch_one_exp = "%s/fetch_one_sop.exp" % portal_location
fetch_mass_exp = "%s/fetch_mass.exp" % portal_location
fetch_reasons_exp = "%s/fetch_reasons.exp" % portal_location
notify_exp = "%s/notify.exp" % portal_location
get_sop_folder_list_exp = "%s/get_sop_folder_list.exp" % portal_location
push_sop_exp = "%s/push_sop.exp" % portal_location
sop_location = "%s/SOP" % portal_location
command_low = '/home/common/ServiceDesk/CompleteCO_Normal.sh'
command_std = '/home/common/ServiceDesk/CompleteCO_Std.sh'
command_task = '/home/common/ServiceDesk/CompleteCOWFTask.sh'
command_task_skip = '/home/common/ServiceDesk/SkipCOWFTask.sh'
get_servers_py = '/home/common/opsware/get_servers.py'
color_error = gtk.gdk.color_parse('red')
color_good = gtk.gdk.color_parse('white')

# Location of scripts in GlobalShell
ack_script = '/home/common/ServiceDesk/AckTicket.sh'
close_script = '/home/common/ServiceDesk/CloseTicket.sh'
silence_script = '/home/common/DisableAlertNotifications.sh'
co_wiz_script = '/home/common/ServiceDesk/CreateCOWiz.sh'
listopentickets_script = '/home/common/ServiceDesk/ListOpenTickets.sh'

opsware_server = "punifiops030.usa-ed.net"
server_list = "/opsw/Server/\@"
ssh_config_file = "%s/.ssh/config" % home
translation_file = "%s/server_name_translations.txt" % portal_location
rh_exp = "%s/rh.exp" % portal_location
gs_exp = "%s/gs.exp" % portal_location
gs_cmd_exp = "%s/gs_cmd.exp" % portal_location
silence_exp = "%s/silence.exp" % portal_location
faillog = "/home/common/FixFaillog.sh"
notify_py = "%s/notify.py" % portal_location
notify_file = "%s/notify.txt" % portal_location
reasons_file = "%s/reasons.txt" % portal_location
daemonize_py = "%s/daemonize.py" % portal_location
get_server_match_py = "%s/get_server_match.py" % portal_location
silence_py = "%s/silence.py" % portal_location
completeco_py = "%s/completeco.py" % portal_location
createco_py = "%s/createco.py" % portal_location
launch_co_wiz_exp = "%s/launch_co_wiz.exp" % portal_location
mass_tickets_file = "%s/mass_tickets.txt" % portal_location

###################################################################
#               KEYWORDS
###################################################################
# Here you can customize which keyword is used to launch each activity
# ONLY change the part between the " "
keyword_help = "help"
keyword_ack = "ack"
keyword_close = "close"
keyword_ackclose = "kill"
keyword_translation = "trans"
keyword_rosh = "rh "
keyword_gs = "gs"
keyword_silence = "silence"
keyword_update = "update"
keyword_ldap = "ldap"
keyword_ssh = "ssh"
keyword_faillog = "faillog"
keyword_notify = "notify"
keyword_completeco = "co"
keyword_createco = "createco"
keyword_mass = "mass"
# END STATIC
