#!/usr/bin/env python3
"""
Handy python script to facilitate quickly logging into various servers via ssh.
"""

#import getpass
import os
import sys
import time
import traceback
import pexpect

MK1_PASSWORD = "oelinux123"

def setup_my_prefs(child):
    """
    Use expect to send commands to set some prefs on the drone
    """
    command_list = ['alias ls=\'ls -F\'', "alias ll='ls -l'", "cd /usr/local/tealflasher/images"]
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

def screen_to_radio(child):
    """"
    After connecting via SSH, use screen to connect to the radio via uart
    """


#    command_list = ['screen /dev/ttyHS3 115200', '', 'admin', 'teamteal']
#    cmd_error = 'try again'
#    for cmd in command_list:
#        #now we should be sending the password
#        child.sendline(cmd)
#        i = child.expect([pexpect.TIMEOUT, cmd_error, 'userDevice login:', 'admin', 'teamteal'])
#        if i == 0: #timeout
#            print('ERROR!')
#            print('PREF COMMAND FAILED:')
#            print(child.before, child.after)
##            return None
#        if i == 1: #
#            print('Some Other Error! ('+ cmd  +')')
#            continue
#        if i == 2: # userDevice login
#            print('Screen started')
#            continue
#        if i == 3: '
#            
#        else:
#            print('What?')
#    return None

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


def ssh(user, host, passwords):
    """
    Use expect to issue ssh command
    """
    #define some variables
    ssh_newkey = 'Are you sure you want to continue connecting'
    ssh_wrongkey = 'Host key verification failed.'
    ssh_command = ''
    ssh_device_offline = 'No route to host'
    ssh_command = ('/usr/bin/ssh -l %s %s'%(user, host))

    child = pexpect.spawn(ssh_command)

    while True:
        i = child.expect([pexpect.TIMEOUT, ssh_newkey, ssh_wrongkey,
                          '[#$]', 'Connection refused', ssh_device_offline, 'password: '])
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
            print('LOGGED IN.')
            #print(child.before, child.after)
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
            print('Got Password Request')
            #print(child.before, child.after)
            break

    child = ssh_password(child, passwords)
    setup_my_prefs(child)

    return child

def show_help():
    print("{} [opts] <host>".format("sshmk1.sh"))
    print("\t-h: Show help")
    print("\t-i: Copy image to drone image dir")
    print("\t-r: connect to Microhard radio")

def main(opts, args):
    """
    Do the stuff
    """
    # vars
    lin, col = os.popen('stty size', 'r').read().split()
    # resize_command="COLUMNS=" + col + ";LINES=" + lin + ";export COLUMNS LINES;\n"
    host = args[0]

    user = 'root'
    #passwords = ['oelinux123', 'pw2', 'pw3']
    passwords = [MK1_PASSWORD, 'pw2', 'pw3']
    ssh_clearkey = 'ssh-keygen -f "' + os.path.expanduser("~") + \
        '/.ssh/known_hosts" -R ' + host + ' &>/dev/null'

    # clear any existing key to facilitate quickly moving from device to device,
    # or same device with new keys
    os.system(ssh_clearkey)

    if "-i" in opts:
        image_file = args[1]
        scp_image_to_drone(image_file, host)
        sys.exit(0)


    # make connection
    child = ssh(user, host, passwords)
    if child is None:
        print('Could Not Login.')
        sys.exit(1)


    if "-r" in opts:
        screen_to_radio(child)



    # do some shell stuff then call interact to hook up stdout, err, in, etc. to the calling shell.
    child.setwinsize(int(lin), int(col))
    child.interact()

if __name__ == '__main__':
    try:
        opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
        args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

        if len(args) < 1 or "-h" in opts:
            show_help()
            sys.exit(1)

        main(opts, args)
    except(Exception) as e:
        print(str(e))
        traceback.print_exc()
        sys.exit(1)


