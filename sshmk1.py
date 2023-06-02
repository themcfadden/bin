#!/usr/bin/env python3
"""
 python script to facilitate quickly logging into various servers via ssh.
"""

#import getpass
import os
import sys
import time
import traceback
import pexpect

MK1_PASSWORD = "oelinux123"

def cd_to_image_dir(child):
    """"
    CD to the image directory, a common need
    """
    image_dir = "/usr/local/tealflasher/images"
    return cd_to_dir(child, image_dir)

def cd_to_dir(child, directory):
    """"
    CD to the specified directory, a common need
    """

    if len(directory) < 1:
        print("Directory not specified");
        return None

    cmd = "cd " + directory
    child.sendline(cmd)

    resp = child.expect([pexpect.TIMEOUT, '[#$]'])
    if resp != 1:
        print("Did not get to path")
        print(child.before, child.after)
        return None

    print("CD to images dir.")

    return child

def setup_my_prefs(child):
    """
    Use expect to send commands to set some prefs on the drone
    """
    command_list = ['alias ls=\'ls -F\'', "alias ll='ls -l'", "alias systemctl='systemctl --no-pager'", "cd /data/teal",
                    "alias pst='ps | grep teal'"]
    cmd_error = 'try again'
    did_something = False
    for cmd in command_list:
        #now we should be sending the password
        child.sendline(cmd)
        i = child.expect([pexpect.TIMEOUT, cmd_error, '[#$]'])
        if i == 0: #timeout
            print('ERROR!')
            print('PREF COMMAND FAILED:')
            print(child.before, child.after)
        if i == 1: #
            print('Some Other Error! ('+ cmd  +')')
            continue
        if i > 1: #success
            did_something = True

    if did_something:
        print('PREFS SET!')
    return None


def ssh_password(child, passwords):
    """
    Use expect to send passwords and process reponse
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
    print(ssh_cmd_string)
    child.sendline(ssh_cmd_string)

    resp = child.expect([pexpect.TIMEOUT, '[#$]'])
    if resp != 1:
        print("Did not get to path")
        print(child.before, child.after)
        return None

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


def scp(user, host, image_file, destination, passwords):
    ssh_command_string = ('/usr/bin/scp %s %s@%s:%s'%(image_file, user, host, destination))
    ssh_command(ssh_command_string, passwords)

def main(opts, args):
    """
    Do the stuff
    """
    # vars
    lin, col = os.popen('stty size', 'r').read().split()
    # resize_command="COLUMNS=" + col + ";LINES=" + lin + ";export COLUMNS LINES;\n"

    if "-q" in opts:
        host = "192.168.168.222"
    else:
        host = args[0]

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

    setup_my_prefs(child)

    if "-i" in opts:
        cd_to_image_dir(child)

    if "-d" in opts:
        cd_to_dir(child, args[1])

    if "-c" in opts:
        child.sendline(args[1])

    if "-g" in opts:
        path_name = args[1]
        file_name = os.path.basename(args[1])
        print("path_name:", path_name)
        print("file_name:", file_name)
        cd_to_image_dir(child)
        ssh_cli_command(child, "rm /usr/local/tealflasher/images/teal_gimbal_*\.bin")
        print("scping file")
        scp(user, host, path_name, "/usr/local/tealflasher/images/" + file_name, passwords)
        ssh_cli_command(child, "cd ..")
        ssh_cli_command(child, "./tealflasher.sh gimbal")

    if "-f" in opts:
        path_name = args[1]
        file_name = os.path.basename(args[1])
        print("path_name:", path_name)
        print("file_name:", file_name)
        cd_to_image_dir(child)
        ssh_cli_command(child, "rm /usr/local/tealflasher/images/teal_fmu-v5-mk1_*\.bin")
        print("scping file")
        scp(user, host, path_name, "/usr/local/tealflasher/images/" + file_name, passwords)
        ssh_cli_command(child, "cd ..")
        ssh_cli_command(child, "./tealflasher.sh fmu")

    # do some shell stuff then call interact to hook up stdout, err, in, etc. to the calling shell.
    child.setwinsize(int(lin), int(col))
    child.interact()

def show_help():
    print("{} [opts] <host>".format("sshmk1.py"))
    print("\t-h: Show help")
    print("\t-i: automatically move image dir")
    print("\t-d: cd to specified directory")
    print("\t-g: program gimbal <gimbal_fw.bin>")
    print("\t-f: program fmu <fmu_fw.bin>")
    print("\t-q: quickly use default ip address of 192.168.168.222")

if __name__ == '__main__':
    try:
        opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
        args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

        if len(args) < 1:
            if "-h" in opts or "-q" not in opts:
                show_help()
                sys.exit(1)
            if "-g" in opts:
                if len(args) != 1:
                    print("-g options requires a gimbal file")
                    sys.exit(1)

        main(opts, args)

    except(Exception) as e:
        print(str(e))
        traceback.print_exc()
        sys.exit(1)

