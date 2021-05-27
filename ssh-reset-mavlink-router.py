#!/usr/bin/env python3

"""
SSH systemctl restart mavlink-router.
Usage: ssh-reset-mavlink-router.py
"""

import os
import sys
import time
import traceback
import pexpect

MK1_PASSWORD = "oelinux123"

def ssh_password(child, passwords):
    """
    Use expect to send passwords and process response
    """
    ssh_pass_fail = 'try again.'
    for password in passwords:
        #now we should be sending the password
        child.sendline(password)
        i = child.expect([pexpect.TIMEOUT, ssh_pass_fail, '[#$]'])
        if i == 0: #timeout
            print('ERROR!')
            print('SSH COULD NOT LOGIN:')
            print(child.before, child.after)
            return None
        if i == 1: #wrong password
            print('Wrong Password! ('+ password +')')
            continue
        if i == 2: #success
            print('SUCCESS LOGGING IN!')
            return child
    return None

def ssh_cli_command(child, ssh_cmd_string):
    #print(ssh_cmd_string)
    child.sendline(ssh_cmd_string)

    resp = child.expect([pexpect.TIMEOUT, '[#$]'])
    if resp != 1:
        print("Did not get to path")
        print(child.before, child.after)
        return None
    
    return child

def ssh_command(ssh_command_string, passwords):
    """
    Use expect to issue ssh command
    """
    #define some variables
    ssh_newkey = 'Are you sure you want to continue connecting'
    ssh_wrongkey = 'Host key verification failed.'
    ssh_device_offline = 'No route to host'
    #ssh_last_login = "Last login:"

    child = pexpect.spawn(ssh_command_string)

    while True:
        i = child.expect([pexpect.TIMEOUT, ssh_newkey, ssh_wrongkey,
                          '[#$]', 'Connection refused', ssh_device_offline,
                          'password: '])
        if i == 0: # Timeout
            print('ERROR!')
            print('SSH could not login. Here is what SSH said:')
            print(child.before, child.after)
            return None
        if i == 1: # SSH does not have the public key. Just accept it.
            #print(child.before, child.after)
            child.sendline('yes')
            time.sleep(0.1)
        elif i == 2:
            print('KEY CHANGE. HANDLE THIS SCENARIO.')
            #print(child.before, child.after)
            sys.exit(1)
            #child.close(force=True)
            #child = pexpect.spawn(ssh_command)
            #continue
            return None
        if i == 3: #already logged in and ssh multiplexing is occurring
            print('LOGGED IN (already).')
            #print(child.before, child.after)
            return child
        if i == 7:
            print('LOGGED IN.')
            return child
        if i == 4:
            print('SSH NOT RUNNING ON REMOTE HOST')
            #print(child.before, child.after)
            sys.exit(-1)
        if i == 5:
            print('IP Unreachable')
            #print(child.before, child.after)
            sys.exit(-1)
        elif i == 6:
            #print('Got Password Request')
            #print(child.before, child.after)
            break

    child = scp_password(child, passwords)

    return child

def scp_password(child, passwords):
    """
    Use expect to send passwords and process response
    """
    ssh_pass_fail = 'try again.'
    for password in passwords:
        #now we should be sending the password
        child.sendline(password)

        i = child.expect([pexpect.TIMEOUT, ssh_pass_fail, '100%', '[#$]'])
        if i == 0: #timeout
            print('ERROR!')
            print('SSH COULD NOT LOGIN:')
            print(child.before, child.after)
            return None
        if i == 1: #wrong password
            print('Wrong Password! ('+ password +')')
            continue
        if i == 2: #success
            #print('FILE COPIED')
            return child
        if i == 3: #success
            #print('LOGGED IN')
            return child
    return None

def main(opts, args):
    """
    Do the stuff
    """
    # vars
    lin, col = os.popen('stty size', 'r').read().split()
    # resize_command="COLUMNS=" + col + ";LINES=" + lin + ";export COLUMNS LINES;\n"

    host = "192.168.1.222"
    user = 'root'
    passwords = [MK1_PASSWORD, 'oelinux123', 'pw3']
    ssh_clearkey = 'ssh-keygen -f "' + os.path.expanduser("~") + \
        '/.ssh/known_hosts" -R ' + host + ' &>/dev/null'

    # clear any existing key to facilitate quickly moving from device to device,
    # or same device with new keys
    os.system(ssh_clearkey)

    # make connection
    ssh_command_string = ('/usr/bin/ssh -l %s %s'%(user, host))

    child = ssh_command(ssh_command_string, passwords)

    if child is None:
        print('Could Not Login.')
        sys.exit(1)

    ssh_cli_command(child, "systemctl restart mavlink-router")

    print("mavlink router reset")


if __name__ == '__main__':
    try:
        opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
        args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

        main(opts, args)

    except(Exception) as e:
        print(str(e))
        traceback.print_exc()
        sys.exit(1)


