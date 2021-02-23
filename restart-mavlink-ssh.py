#!/usr/bin/env python3

# This script accesses the drone through ssh to restart mavlink router.
# This is  sometimes required to restart a calibration.
#
#  Teal Drones
#  Created: 01/14/2021
#  Last Edited: 01/14/2021

import paramiko 
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.222', port = 22, username = 'root', password = 'oelinux123') #connect to drone 
ssh.exec_command('systemctl restart mavlink-router')
ssh.close()