#!/usr/bin/expect
# Typical usage: exp.sh oelinux123 ssh root@drone systemctl restart mavlink-router

set timeout 20

set cmd [lrange $argv 1 end]
set password [lindex $argv 0]

eval spawn $cmd
expect "assword:"
send "$password\r"

interact
