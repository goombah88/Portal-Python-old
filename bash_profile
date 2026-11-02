#. /export/home/criderc/.bashrc

#############################
#   Some Useful functions   #
#############################

SERVERS="/opsw/Server/@"
VM="$SERVERS/nunifiunx050/files/root/home/e65791/Desktop"

function rh {
local h=$1;
local H=`ls /opsw/Server/@ | egrep "^($h\$|$h\.)"`;
if [ "$H" = "" ]; then
	echo server $h not found;
else
	shift;
	rosh -l root -n $H $*;
fi
} # end rh

function ack {
TICKETS=`echo $1 | tr "," " "`
IMPACT=$2
[[ -z $IMPACT ]] && IMPACT="5"
if [[ -z $TICKETS ]] || [[ -z $IMPACT ]]; then
	echo "ack <ticket#,ticket#,ticket#...> <impact>"
else
	for TICKET in $TICKETS; do
		echo "Acknowledging ticket # $TICKET"
		/home/common/ServiceDesk/AckTicket.sh $TICKET Crider,Chad -I $IMPACT 2>/dev/null
		[[ $? -eq 249 ]] && echo "Retrying..." && /home/common/ServiceDesk/AckTicket.sh $TICKET Crider,Chad -I $IMPACT
	done
fi
} # end ack

function close {
TICKETS=`echo $1 | tr "," " "`
TEXT=$2
if [[ -z $1 ]] || [[ -z $2 ]]; then
	echo "close <ticket#,ticket#,ticket#...> <impact>"
else
	for TICKET in $TICKETS; do
		echo "Closing ticket # $TICKET"
		/home/common/ServiceDesk/CloseTicket.sh $TICKET $TEXT 2>/dev/null
		[[ $? -eq 249 ]] && echo "Retrying..." && /home/common/ServiceDesk/CloseTicket.sh $TICKET $TEXT
	done
fi
} # end close

function console {
/opt/upr/etc/console/$1
} # end console

function resetpass {
#/home/common/passwd.sh e63161 -s sqdelmfi30 -M -p GenPwd
if [[ -z $1 ]] || [[ -z $2 ]]; then
	echo "Usage -> resetpass <userid> <servers>"
	echo "-M and \"-p GenPwd\" are always used."
else
	CMD="/home/common/passwd.sh $1 -s $2 -M -p GenPwd"
	$CMD
	[[ $? -eq 249 ]] && echo "Retrying..." && $CMD
fi
} # end resetpass

function silence {
#/home/common/DisableAlertNotifications.sh nunifidoc999 now 1 -r "reboot"
if [[ -z $1 ]] || [[ -z $2 ]]; then
	echo "Usage -> silence <server> <duration> \"<reason>\""
	echo "\"now\" is always used."
else
	CMD="/home/common/DisableAlertNotifications.sh $1 now $2 -r $3 2>/dev/null"
	$CMD 
	[[ $? -eq 249 ]] && echo "Retrying..." && $CMD $1 now $2 -r $3
fi
} # end silence

alias u='uname -a'
alias dom='domainname'
alias ssh="ssh -o StrictHostKeyChecking=no"
alias nbugui='/usr/openv/netbackup/bin/jnbSA &'
alias inq='/opt/emcgrab/tools/bin/inq.sol64'
alias x='sudo -s'
alias functions=''
alias reg='stty rows 71 columns 27'
alias tall='stty rows 76 columns 87'
hostname >/dev/null 2>&1
[[ $? -ne 0 ]] && alias vi='vim'
alias syncover='rsync -av --delete --progress ~/python/ /opsw/Server/\@/nunifiunx050/files/root/home/e65791/Desktop/python/; rh nunifiunx050 "chown -R e65791:e65791 /home/e65791/Desktop/python/; chmod -R 777 /home/e65791/Desktop/python/*"'
alias syncback='rsync -av --delete --progress /opsw/Server/\@/nunifiunx050/files/root/home/e65791/Desktop/python/Theme_Aggregator/ ~/python/Theme_Aggregator/; rsync -av --delete --progress /opsw/Server/\@/nunifiunx050/files/root/home/e65791/Desktop/python/Bean_Backup/ ~/python/Bean_Backup/'

EDITOR=vi
export EDITOR


RED="\[\033[0;31m\]"
YELLOW="\[\033[1;33m\]"
END_COLOR="\[\033[0m\]"

# export PROMPT_COMMAND='echo -ne "\033]0;${USER}@${HOSTNAME%%.*}:${PWD/#$HOME/~}"; echo -ne "\007"'
# export FQDN=`cat /etc/hosts | grep -v "#" | grep $(hostname) | awk '{print $2}'`
export FQDN=`cat /etc/hosts | grep -v "#" | grep globalname | awk '{print $2}'`

if [ "`id | awk -F= -F\( '{print $1}' | awk -F= '{print $2}'`" == "0" ]; then
       USER="\[\033[1;34m\]root"
else
       USER=""
fi

if [[ `uname -a | awk '{print $2}'` =~ "punifiops0.*" ]]; then
	HOST=`hostname`
	if [[ `uname -a | awk '{print $1}'` == "Linux" ]]; then
		RELEASE="Linux `cat /etc/redhat-release | awk '{print $7}'`"
	elif [[ `uname -a | awk '{print $1}'` == "SunOS" ]]; then
		RELEASE="Solaris `cat /etc/release | grep Solaris | awk -F_ '{print $2}' | sed 's/...$//'`"
	fi
else
	HOST="OPSWARE"
fi

export PROMPT_COMMAND='echo -ne "\033]0;${FQDN}"; echo -ne "\007"'

# export PS1='\u@\h:\w\$ '
# export PS1="\n\[\033[1;36m\]\u\[\033[1;37m\] \[\033[0;36m\]`date`\n\[\033[0m\][\[\033[1;33m\]\w\[\033[0m\]] "
# export PS1="\n\[\033[1;36m\]\u\[\033[1;37m\] \[\033[1;33m\]\h \[\033[0;36m\]`uname` `uname -r` `domainname` \n\[\033[0m\][\[\033[1;33m\]\w\[\033[0m\]] "

hostname >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
	export PS1="\h:\w>"
else
	export PS1="$USER \[\033[1;33m\]$HOST $RELEASE \n\[\033[0;36m\][\[\033[1;36m\]\w\[\033[0;36m\]]\[\033[0m\]\n--> "
fi

export GREP_COLOR='1;30;43'
export LC_COLLATE=en_US
#export LANG=en_US.UTF-8
export LANG="C"
#export LC_CTYPE=en_US.UTF-8
#export LC_ALL=C

## Set up paths
export PATH="/bin:/sbin:/opsw/bin:/usr/ccs/bin:/usr/bin:/usr/lib:/usr/sbin:/usr/openv/netbackup/bin:/usr/openv/volmgr/bin:/usr/openv/netbackup/bin/goodies::/usr/local/bin:/etc/opt/SUNWconn/bin:/opt/VRTS/bin:/opt/DTT:/opt/DTT/Bin:/opt/OSOL0chime/bin:/opt/SUNWldm/bin:/opt/coolstack/bin:/opt/coolstack/sbin:/opt/coolstack/apache2/bin:/opt/coolstack/mysql/bin:/opt/coolstack/php5/bin:/usr/local/rrdtool/bin:/usr/perl5/bin:/usr/openv/netbackup/bin/admincmd/:/usr/openv/netbackup/db/shared_scripts:/etc:/usr/platform/sun4v/sbin:/usr/tools/bin:/usr/bin:/usr/local/bin:/usr/tools/emc:/usr/sfw/bin/"
LD_LIBRARY_PATH="/usr/lib:/usr/local/lib:$LD_LIBRARY_PATH:/usr/openwin/lib:/usr/ucblib"

### MISC USEFUL ALIASES ###

alias ll='ls -alh'
alias ls='ls --color="tty"'
alias l.='ls -d .* --color=tty'

export HISTSIZE=3000

# don't put duplicate lines in the history. See bash(1) for more options
export HISTCONTROL=ignoredups
# ... and ignore same sucessive entries.
export HISTCONTROL=ignoreboth

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

if [ -f /etc/bash_completion ]; then
   . /etc/bash_completion
fi
