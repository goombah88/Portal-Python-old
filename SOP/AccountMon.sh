#!/bin/bash
#   ActMon
#   John Stewart
#
#
#
#
#set -x
USERS="facs"
#NOTIFY="<EMAIL>"
NOTIFY="<EMAIL>"
DATE=`date '+%m/%d/%y'`
MSG="From:<AcctMon@UnixTeam>\nTo:<$NOTIFY>\nReply-to:<EMAIL>\nBcc:<EMAIL>\nSubject:FACS ACCOUNT LOCKED on $HOSTNAME\ncontent-Type: text/html;\n\n
<HTML>
<b>ATTENTION</b>:<br><br>FACS Account was found locked on $HOSTNAME on `date '+%m/%d/%y at %R:%S'`<br>
<br><i>This account was Auto-Unlocked, if problems persist please contact unix team.</i>
</HTML>"


for u in $USERS; do
        if [ `passwd -S $u |awk '{print $2}'` == "LK" ]; then

                echo -e $MSG | sendmail -t
                passwd -u $u 2>&1 > /dev/null
                pam_tally --reset --user $u 2>&1 > /dev/null
                echo $u Locked on `date '+%m/%d/%y at %R:%S'`>> /var/log/ActMon

                if [ `cat /var/log/ActMon|grep $DATE | wc -l` -gt 3 ]; then
                        if [ `cat /var/log/ActMon|grep $DATE |grep TICKET| wc -l` -eq 0 ]; then
                                /opt/OV/bin/opcmsg severity="critical" application="FACS" object="FACS" msg_grp="UNXS" msg_text="$HOSTNAME: Repeated facs account lockouts on $HOSTNAME on `date '+%m/%d/%y at %R:%S'`";
                                echo "PRI 1 TICKET Sent to UNIX TEAM on `date '+%m/%d/%y at %R:%S'`" >> /var/log/ActMon
                        fi
                fi
        fi
done

