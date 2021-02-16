#!/usr/bin/env python3
"""
Handy python script to facilitate quickly logging into various servers via ssh.
"""

import os
import sys
import time
import traceback
import pexpect
from pexpect import pxssh

MK1_PASSWORD = "oelinux123"

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

def copy_fmuflash_to_drone(child):
    """
    copy programming script
    """
    child.sendline("cd /usr/local/tealflasher/images")
    resp = child.expect([pexpect.TIMEOUT, '[#$]'])
    if resp != 1:
        print("Did not get to path")
        print(child.before, child.after)
        return None

    child.sendline("chmod +x ./fmuf.sh")
    resp = child.expect([pexpect.TIMEOUT, '[#$]'])
    if resp != 1:
        print("Failed chmod")
        print(child.before, child.after)
        return None

    return child


def issue_program_command(child, image_file):
    """
    issue programming command on Mk1 drone
    """
    prg_cmd = "./fmuf.sh {}".format(image_file)
    command_list = ['cd /usr/local/tealflasher/images', prg_cmd]

    not_found = "not found"
    download_success = "File downloaded successfully"

    for cmd in command_list:
        print("Issuing cmd:", cmd)
        child.sendline(cmd)
        resp = child.expect([pexpect.TIMEOUT, not_found, '[#$]', '=', download_success])
        if resp == 0:
            print('ERROR!')
            print('PREF COMMAND FAILED:')
            print(child.before, child.after)
            return child
        if resp == 1:
            print("Command or file not found")
            print(child.before, child.after)
            return child
        if resp == 2: # command prompt
            continue
        if resp == 3: # '=' shows progress and keeps expect from timing out
            continue
        if resp == 4:
            print("Done")
            return child
    return child


def scp(user, host, image_file, destination, passwords):
    ssh_command_string = ('/usr/bin/scp %s %s@%s:%s'%(image_file, user, host, destination))
    ssh_command(ssh_command_string, passwords)


def ssh(user, host, passwords):
    ssh_command_string = ('/usr/bin/ssh -l %s %s'%(user, host))
    return ssh_command(ssh_command_string, passwords)

#def ssh_command(ssh_cmd_string, user, host, image_file, destination, passwords):
def ssh_command(ssh_cmd_string, passwords):
    """
    Use expect to issue ssh command
    """
    #define some variables
    ssh_newkey = 'Are you sure you want to continue connecting'
    ssh_wrongkey = 'Host key verification failed.'
    ssh_device_offline = 'No route to host'
    ssh_last_login = "Last login:"
    
    #ssh_command = ('/usr/bin/scp %s %s@%s:%s'%(image_file, user, host, destination))
    #print("ssh_cmd_str:", ssh_cmd_string)

    child = pexpect.spawn(ssh_cmd_string)

    while True:
        i = child.expect([pexpect.TIMEOUT, ssh_newkey, ssh_wrongkey,
                          '[#$]', 'Connection refused', ssh_device_offline,
                          'password: '])
        if i == 0: # Timeout
            print('ERROR!')
            print('SSH could not login. Here is what SSH said:')
            #print(child.before, child.after)
            return None
        if i == 1: # SSH does not have the public key. Just accept it.
            print('Asking to accept public key')
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


def main(opts, args):
    """
    Do the stuff
    """

    # vars
    lin, col = os.popen('stty size', 'r').read().split()
    # resize_command="COLUMNS=" + col + ";LINES=" + lin + ";export COLUMNS LINES;\n"
    host = args[0]

    user = 'root'
    passwords = [MK1_PASSWORD, 'pw2', 'pw3']
    ssh_clearkey = 'ssh-keygen -f "' + os.path.expanduser("~") + \
        '/.ssh/known_hosts" -R ' + host + ' &>/dev/null'

    # clear any existing key to facilitate quickly moving from device to device,
    # or same device with new keys
    os.system(ssh_clearkey)

    image_file_path = args[1]
    destination = "/usr/local/tealflasher/images/"

    # make connection
    scp(user, host, image_file_path, destination, passwords)
    scp(user, host, '/home/mattmc/bin/fmuf.sh', destination, passwords)

    child = ssh(user, host, passwords)
    if child is None:
        print('Could Not Login.')
        sys.exit(1)

    if copy_fmuflash_to_drone(child) == None:
        print("Could not make script executable")
        sys.exit(1)

    image_file = os.path.basename(image_file_path)
    print("Programming FMU:", image_file)
    child = issue_program_command(child, image_file)

    # do some shell stuff then call interact to hook up stdout, err, in, etc. to the calling shell.
    child.setwinsize(int(lin), int(col))
    child.interact()

def show_help():
    print("{} <host> <image_file>".format("sshmk1.sh"))
    print("\t-h: Show help")

if __name__ == '__main__':
    try:
        opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
        args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

        if len(args) < 2:
            print("Too few args")
            show_help()
            sys.exit(1)

        if "-h" in opts:
            show_help()
            sys.exit(1)

        main(opts, args)

    except(Exception) as e:
        print(str(e))
        traceback.print_exc()
        sys.exit(1)


