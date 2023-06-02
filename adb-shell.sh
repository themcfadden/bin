#!/usr/bin/env bash

stty_cmd=$(stty size | awk '{print "stty rows "$1 " cols "$2}')

expect -f ~/bin/adb-shell.expect $stty_cmd
