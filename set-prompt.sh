#!/bin/bash

#export PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "

#PS1="\[\033[01;32m\]\u\[\033[00m\]@\[\033[01;32m\]\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "
#export PS1="\[\033[01;33m\]\u\[\033[00m\]@\[\033[01;32m\]\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "


PS1_USERNAME_COLOR=32
PS1_HOSTNAME_COLOR=32
PS1_DIRECTORY_COLOR=34
export PS1="\[\033[01;${PS1_USERNAME_COLOR}m\]\u\[\033[00m\]@\[\033[01;${PS1_HOSTNAME_COLOR}m\]\h\[\033[00m\]:\[\033[01;${PS1_DIRECTORY_COLOR}m\]\w\[\033[00m\]\$ "

echo PS1=${PS1}

