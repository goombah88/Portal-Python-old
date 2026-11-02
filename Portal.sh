#!/bin/bash

# Author: Chad Crider
# Purpose: General purpose tool to simply and unify various commands and tools
# Created: 8/24/2011
# Version: 3.0
#
# Changes: 1/6/2012 - Added a translation file to hold CRS server translations

OPS="punifiops030.usa-ed.net"
SERVER_LIST="/opsw/Server/\@"
SSH_CONFIG_FILE="$HOME/.ssh/config"
TERM_SIZE=" --geometry 87x27"
GOTO="gnome-terminal $TERM_SIZE --disable-factory -x ssh -o StrictHostKeyChecking=no"
TICKET_FILE="/tmp/tickets"
USERID=$USER
PORTAL_LOCATION="/home/e65791/Desktop/Portal"
CONFIG="$PORTAL_LOCATION/.portal.conf"
PASS=`cat $CONFIG`
TRANSLATIONS="$PORTAL_LOCATION/server_name_translations.txt"
RH_LOCATION="$PORTAL_LOCATION/rh.exp"
GS_LOCATION="$PORTAL_LOCATION/gs.exp"
GS_CMD_LOCATION="$PORTAL_LOCATION/gs_cmd.exp"
DM_LOCATION="$PORTAL_LOCATION/daemonize.py"
GM_LOCATION="$PORTAL_LOCATION/get_server_match.py"
SILENCE_PY="$PORTAL_LOCATION/silence.py"
SILENCE_EXP="$PORTAL_LOCATION/silence.exp"
FAILLOG="/home/common/FixFaillog.sh"
NOTIFY="$PORTAL_LOCATION/notify.py"
CO_LOCATION="$PORTAL_LOCATION/complete_co.py"

# Make sure all required files are present
[[ ! -f $RH_LOCATION ]] && zenity --info --text="rh.exp must be in the same directory as Portal.sh"
[[ ! -f $GS_LOCATION ]] && zenity --info --text="gs.exp must be in the same directory as Portal.sh"
if [[ ! -f $TRANSLATIONS ]]; then
    echo "freeparking1 pundfiams010
freeparking2 pundfiams020
spartfi010 punifiart010
test1 nuniarcrs010
prod2 pcra01crsprod2
test3 nuniarcrs030
test4 nuniarcrs040
pcra01crsprod4 puniarcrs040
prod4 puniarcrs040
pcra01crsprod5 puniarcrs050
prod5 puniarcrs050
prod9 puniarcrs090
prod10 puniarcrs100
prod100 puniarcrs100" > $TRANSLATIONS
fi

########################################################################
#
# CHECKING USER INPUT
#
########################################################################

STRING=$(zenity --entry --text="Your wish is my command...")
[[ $? -eq 1 ]] && exit

function ack {
TICKET_ACK=`zenity --entry --text="Ticket #s?"`
[[ $? -eq 1 ]] && exit
[[ -z $TICKET_ACK ]] && ack
TICKET_ACK=`echo $TICKET_ACK | tr "," " "`
IMPACT_ACK=`zenity --entry --text="Impact? (ENTER for 5)" --entry-text="5"`
[[ $? -eq 1 ]] && exit
[[ -z $IMPACT_ACK ]] && ack

DOUBLE_CHECK=`zenity --question --text="Ack ticket(s) $TICKET_ACK with impact $IMPACT_ACK?"; echo $?`
if [[ $DOUBLE_CHECK -eq 0 ]]; then
	#zenity --info --text="Ack'ing ticket(s) $TICKET_ACK with impact $IMPACT_ACK"
	# Add to the ticket file and build command
        for TICKET in $TICKET_ACK; do
		    echo "$TICKET" >> $TICKET_FILE
		    CMD+="ack $TICKET $IMPACT_ACK; "
        done
	gnome-terminal $TERM_SIZE --disable-factory -x $GS_CMD_LOCATION $PASS "$CMD"
else
	exit 1
fi
} # end ack

function close {
TICKET_CLOSE=`zenity --entry --text="Ticket #s?"`
[[ $? -eq 1 ]] && exit
[[ -z $TICKET_CLOSE ]] && close
TICKET_CLOSE=`echo $TICKET_CLOSE | tr "," " "`
REASON=`zenity --entry --text="Reason for closing ticket"`
[[ $? -eq 1 ]] && exit
[[ -z $REASON ]] && close

DOUBLE_CHECK=`zenity --question --text="Close ticket(s) $TICKET_CLOSE with reason - \"$REASON\"?"; echo $?`
if [[ $DOUBLE_CHECK -eq 0 ]]; then
	#zenity --info --text="Closing ticket(s) $TICKET_CLOSE with reason $REASON"
        for TICKET in $TICKET_CLOSE; do
		# Remove from the ticket file
		sed -i "/^$TICKET$/d" $TICKET_FILE

		CMD+="close $TICKET \"$REASON\"; "
        done
	gnome-terminal $TERM_SIZE --disable-factory -x $GS_CMD_LOCATION $PASS "$CMD"
else
	exit 1
fi
} # end close

function ack_close {
TICKET_ACK_CLOSE=`zenity --entry --text="Ticket #s?"`
[[ $? -eq 1 ]] && exit
[[ -z $TICKET_ACK_CLOSE ]] && close
TICKET_ACK_CLOSE=`echo $TICKET_ACK_CLOSE | tr "," " "`
REASON=`zenity --entry --text="Reason for closing ticket"`
[[ $? -eq 1 ]] && exit
[[ -z $REASON ]] && ack_close

DOUBLE_CHECK=`zenity --question --text="Close ticket(s) $TICKET_ACK_CLOSE with reason - \"$REASON\"?"; echo $?`
if [[ $DOUBLE_CHECK -eq 0 ]]; then
	#zenity --info --text="Closing ticket(s) $TICKET_ACK_CLOSE with reason $REASON"
        for TICKET in $TICKET_ACK_CLOSE; do
		CMD+="ack $TICKET 5; close $TICKET \"$REASON\"; "
        done
	gnome-terminal $TERM_SIZE --disable-factory -x $GS_CMD_LOCATION $PASS "$CMD"
else
	exit 1
fi
} # end ack_close

function change_passwd {
PASS_USER=`zenity --entry --text="User ID? (case sensitive)"`
[[ $? -eq 1 ]] && exit
[[ -z $PASS_USER ]] && ack
PASS_SERVERS=`zenity --entry --text="Server name(s)? (comma separated)"`
[[ $? -eq 1 ]] && exit
[[ -z $PASS_SERVERS ]] && ack
PASS_EXPIRE=`zenity --question --text="Expire account?\n\n(Cancel will set NoExpire option)"`
[[ $? -eq 0 ]] && EXPIRE="" || EXPIRE="NoExpire"

DOUBLE_CHECK=`zenity --question --text="Command to run - passwd.sh $PASS_USER -M -s $PASS_SERVERS -p GenPwd $EXPIRE ?"; echo $?`
if [[ $DOUBLE_CHECK -eq 0 ]]; then
	#zenity --info --text="Ack'ing ticket(s) $TICKET_ACK with impact $IMPACT_ACK"
	# Add to the ticket file and build command
    CMD="/home/common/AccSec/passwd.sh $PASS_USER -M -s $PASS_SERVERS -p GenPwd $EXPIRE"
	gnome-terminal $TERM_SIZE --disable-factory -x $GS_LOCATION $PASS "$CMD"
else
	exit 1
fi
} # end change_passwd

######################
#		             #
#  Check the input   #
#                    #
######################

if [[ $STRING == update ]]; then
	#HOSTS=`ssh -p 2222 $OPS ls $SERVER_LIST`
	#gnome-terminal $TERM_SIZE --disable-factory -x $RH_LOCATION $PASS
	HOSTS=`$RH_LOCATION $PASS "/home/common/opsware/get_servers.py"`
    echo "$HOSTS" > /tmp/hosts
    dos2unix /tmp/hosts
    sed '1,/get_servers.py/ d' /tmp/hosts > /tmp/hosts2
    egrep -v "Cirrus|Template|~>" /tmp/hosts2 | sort -n -k2 > /tmp/hosts

	# Clean out file first
	cat /dev/null > $SSH_CONFIG_FILE

	for HOST in `cat /tmp/hosts`; do
		echo "Host $HOST" >> $SSH_CONFIG_FILE
	done
	zenity --info --text="Server list updated..\n\nNew file:\n`ls -lh $SSH_CONFIG_FILE | cut -d" " -f 6-10`\n\nServer Count: `cat /tmp/hosts | wc -l`"
elif [[ $STRING == help ]]; then
    zenity --info --text="Possible keywords/commands:\n\n<b>ack</b> - Acknowledge ticket(s)\n<b>close</b> - Close ticket(s)\n<b>kill</b> - Ack and Close ticket(s)\n<b>update</b> - update serverlist from globalshell\n<b>silence</b> - Completely silence a server for a given\n\t\tamount of time\n<b>ldap</b> - ssh's you to punifirds010\n<b>gs</b> - opens globalshell window\n<b>ssh</b> - takes you to spsshfi100\n<b>rh \"server\"</b> - opens globalshell and rosh's you into\n\t\t\t a server as root\n\t\t     - checks the server translations file for\n\t\t\tmatches first\n<b>\"server name\"</b> - ssh to the given server as yourserlf\n                (can type partial names and it will list matches)\n<b>trans</b> - displays the server translations file for editing\n<b>tickets</b> - \"not currently implemented\"\n<b>passwd</b> - Reset a user's password on server(s)\n<b>help</b> - this help screen\n\n<b>All options open in a new window</b>"
elif [[ $STRING == silence ]]; then
	SERVER=`zenity --entry --text="Server to silence:"`
	[[ $? -eq 1 ]] && exit
    if [[ `grep $SERVER $SSH_CONFIG_FILE | wc -l` -eq 1 ]]; then
    	# Found an EXACT match
    	HOST=`cat $SSH_CONFIG_FILE | grep $SERVER | awk '{print $2}'`
        $SILENCE_PY $HOST
        #DURATION=`zenity --scale --text="How long to silence server?" \
        #--value=1 --min-value=1 --max-value=72`
        #[[ $? -eq 1 ]] && exit
        #REASON=`zenity --entry --text="Reason for setting the silence" \
        #--entry-text="Reboot"`
        #[[ $? -eq 1 ]] && exit
	    #gnome-terminal $TERM_SIZE --disable-factory \
        #-x $SILENCE_EXP "silence $HOST $DURATION \"$REASON\""
    elif [[ `grep $SERVER $SSH_CONFIG_FILE | wc -l` -gt 1 ]]; then
    	# No EXACT match found
        # Launch python script
        $SILENCE_PY $SERVER
#    	MATCHES=`$GM_LOCATION $SERVER`
#        for MATCH in $MATCHES; do
#            CMD="$FAILLOG $MATCH; "
#        done
#	    gnome-terminal $TERM_SIZE --disable-factory -x $SILENCE_EXP "$CMD"
    else
    	zenity --error --text="No match found. Try again."
    	exit 1
    fi

elif [[ $STRING == ldap ]]; then
	host=`cat $SSH_CONFIG_FILE | grep punifirds010 | awk '{print $2}'`
	$GOTO $host
elif [[ $STRING == gs ]]; then
	gnome-terminal $TERM_SIZE --disable-factory -x $GS_LOCATION $PASS
elif [[ $STRING == ssh ]]; then
	$GOTO punifissh010.usa-ed.net
elif [[ $STRING =~ "^rh " ]]; then
	ROSH_TO=`echo $STRING | awk '{print $2}' | tr [A-Z] [a-z]`

    # Check the translations file first
	if [[ `cat $TRANSLATIONS | awk '{print $1}' | grep ^$ROSH_TO$` ]]; then
        while read LINE; do 
            SHORT=`echo $LINE | awk '{print $1}'`
            LONG=`echo $LINE | awk '{print $2}'`
            if [[ $SHORT == $ROSH_TO ]]; then 
                # Found a match, rh to it
	            gnome-terminal $TERM_SIZE --disable-factory -x $RH_LOCATION $PASS "rh $LONG"
            fi
        done < "$TRANSLATIONS"
    else
        # Now check the server list file
        if [[ `grep $ROSH_TO $SSH_CONFIG_FILE | wc -l` -eq 1 ]]; then
    		# Found an EXACT match
    		HOST=`cat $SSH_CONFIG_FILE | grep $ROSH_TO | awk '{print $2}'`
    	    gnome-terminal $TERM_SIZE --disable-factory -x $RH_LOCATION $PASS "rh $HOST"
    	elif [[ `grep $ROSH_TO $SSH_CONFIG_FILE | wc -l` -gt 1 ]]; then
    		# No EXACT match found
            # show all matches
    		$DM_LOCATION $ROSH_TO
    	else
    		zenity --error --text="No match found. Try again."
    		exit 1
    	fi
    fi
elif [[ $STRING == "ack" ]]; then
	ack
elif [[ $STRING == "close" ]]; then
	close
elif [[ $STRING == "kill" ]]; then
	ack_close
elif [[ $STRING == "tickets" ]]; then
	NEW=`zenity --text-info --filename=$TICKET_FILE --editable`
	echo "$NEW" > $TICKET_FILE
elif [[ $STRING == "trans" ]]; then
	NEW=`zenity --text-info --filename=$TRANSLATIONS --editable`
elif [[ $STRING == "passwd" ]]; then
	change_passwd
elif [[ $STRING == "faillog" ]]; then
    SERVER=`zenity --entry --text="Which server?"`
    [[ $? -eq 1 ]] && exit
    # Check the translations file first
	if [[ `cat $TRANSLATIONS | awk '{print $1}' | grep ^$SERVER$` ]]; then
        while read LINE; do 
            SHORT=`echo $LINE | awk '{print $1}'`
            LONG=`echo $LINE | awk '{print $2}'`
            if [[ $SHORT == $SERVER ]]; then 
                # Found a match, rh to it
	            gnome-terminal $TERM_SIZE --disable-factory \
                -x $GS_LOCATION $PASS "$FAILLOG $LONG"
            fi
        done < "$TRANSLATIONS"
    else
        # Now check the server list file
        if [[ `grep $SERVER $SSH_CONFIG_FILE | wc -l` -eq 1 ]]; then
    		# Found an EXACT match
    		HOST=`cat $SSH_CONFIG_FILE | grep $SERVER | awk '{print $2}'`
	        gnome-terminal $TERM_SIZE --disable-factory \
            -x $GS_LOCATION $PASS "$FAILLOG $HOST"
    	elif [[ `grep $SERVER $SSH_CONFIG_FILE | wc -l` -gt 1 ]]; then
    		# No EXACT match found
            # show all matches
    		MATCHES=`$GM_LOCATION $SERVER`
            for MATCH in $MATCHES; do
                CMD="$FAILLOG $MATCH; "
            done
	        gnome-terminal $TERM_SIZE --disable-factory -x $GS_LOCATION $PASS "$CMD"
    	else
    		zenity --error --text="No match found. Try again."
    		exit 1
        fi
    fi
elif [[ $STRING == "notify" ]]; then
    SERVER=`zenity --entry --text="Which server?"`
    [[ $? -eq 1 ]] && exit
    # Check the translations file first
	if [[ `cat $TRANSLATIONS | awk '{print $1}' | grep ^$SERVER$` ]]; then
        while read LINE; do 
            SHORT=`echo $LINE | awk '{print $1}'`
            LONG=`echo $LINE | awk '{print $2}'`
            if [[ $SHORT == $SERVER ]]; then 
                # Found a match, use it
	            $NOTIFY $LONG
            fi
        done < "$TRANSLATIONS"
    else
        # Now check the server list file
        if [[ `grep $SERVER $SSH_CONFIG_FILE | wc -l` -eq 1 ]]; then
    		# Found an EXACT match
    		HOST=`cat $SSH_CONFIG_FILE | grep $SERVER | awk '{print $2}'`
            $NOTIFY $HOST
    	elif [[ `grep $SERVER $SSH_CONFIG_FILE | wc -l` -gt 1 ]]; then
    		# No EXACT match found
            # show all matches
    		MATCH=`$GM_LOCATION $SERVER`
	        $NOTIFY $MATCH
    	else
    		zenity --error --text="No match found. Try again."
    		exit 1
        fi
    fi
elif [[ $STRING == "co" ]]; then
    $CO_LOCATION
else
	# Take the shortname entered and get the FQDN
	# and ssh to it in another window
	STRING=`echo $STRING | tr [A-Z] [a-z]`
	if [[ `grep $STRING $SSH_CONFIG_FILE | wc -l` -eq 1 ]]; then
		# Found an EXACT match
		host=`cat $SSH_CONFIG_FILE | grep $STRING | awk '{print $2}'`
		$GOTO $host
	elif [[ `grep $STRING $SSH_CONFIG_FILE | wc -l` -gt 1 ]]; then
		# No EXACT match found
		CHOICE=$(zenity --width=350 --height=400 \
		--title="Pick the right server name" \
		--list \
		--radiolist \
		--text="Possible Matches:" \
		--column=Action \
		--column="Choice" $(for i in `cat $SSH_CONFIG_FILE | awk '{print $2}' | grep $STRING`; do echo "FALSE $i"; done))
		[[ $? -eq 1 ]] && exit
		$GOTO $CHOICE
	else
		zenity --error --text="No match found. Try again."
	fi
fi
