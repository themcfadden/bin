from invoke import task
import os
import sys
import pexpect
from pexpect.exceptions import TIMEOUT
import time

from io import StringIO

"""
Invoce reminders:
- @task decorator to define an exported task
  Function name uses underscores, command name translates them dashes

- Function arguments become flags. If no default value, it is assumed to be
  a string.

  @task
  def hi(ctx, name):
     print("Hi {}".format(name))

  Can be:
  $ invoke hi Name
  $ invoke hi --name Name
  $ invoke hi --name=Name
  $ invoke hi -n Name
  $ invoke hi -nName

- Metadata via @task
  - @task(help={'name': "Name of the person to say hi to"})
    def hi(ctx, name):
    <triple quote>
    Say hi to someone.
    <triple quote>


  $ inv --help hi
  Usage: inv[oke] [--core-opts] hi [--options] [other tasks here...]

  Docstring:
    Say hi to someone

  Options:
    -n STRING, --name=STRING Name of person to say hi to.

- invoke --list
- Run shell commands with:
  ctx.run(quoted command)
- Declar pre-tasks
  @task(<name-of-invoke-task>)


"""


#@task(help={'postfix_name':'Name to append to file - usually version info'})
#def px4_update_name(ctx, postfix_name):
#    """
#    Copy px4 bin with a new name
#
#    Args:
#        postfix_name (string): version info to append to string
#    example: inv px4-update-name 1.9.13-01
#    """
#    # Make something to use to grab the output from the run so I can parse it.
#    mystdout = StringIO()
#
#    # 1. check for correct directory. Should see build directory
#    ctx.run('ls -d */', out_stream=mystdout)
#    lines = mystdout.getvalue().splitlines()
#    if not "build/" in lines:
#        print("Build dir not found. Are you in the project root?")
#        return
#
#    mystdout.flush()
#    mystdout.truncate(0)
#
#    # 2. build up new name. Use param
#    new_name = 'teal_fmu-v5-mk1_' + postfix_name + '.bin'
#    # 3. Figure out file names
#    bin_path = './build/teal_fmu-v5-mk1_default/'
#    src = bin_path + 'teal_fmu-v5-mk1.bin'
#    dst = bin_path + new_name
#    # 4. Copy existing to new name
#    print('copy bin as:\n->', dst)
#    ctx.run('cp {} {}'.format(src, dst))
#    # 5. Optionally copy to image dir
#    image_dst = '../../reference/images/{}'.format(new_name)
#    ctx.run('cp {} {}'.format(src, image_dst))
#
#    # 6. check
#
#    ctx.run('ls -lF {}'.format(dst), out_stream=mystdout)
#    ctx.run('ls -lF {}'.format(image_dst), out_stream=mystdout)
#
#    #sys.stdout = old_stdout
#    lines = mystdout.getvalue().splitlines()
#
#    print("bin files:")
#    for line in lines:
#        print("->", line)

@task
def px4_update_name(ctx, version_info, move_to_images=False):
    """
    Copy px4 default bin with a new name

    Args:
        postfix_name (string): version info to append to string
        -m to move to reference dir

    Example: inv px4-update-name v1.9.13-01 -m
    """

    file_source_name = "teal_fmu-v5-mk1.bin"

    file_extension = ".bin"
    file_base_name = "teal_fmu-v5-mk1"
    if len(version_info) != 0:
        file_detail_name = "_" + version_info
    else:
        file_detail_name = ""

    dest_file_name = file_base_name + file_detail_name + file_extension
    print("Dest name:", dest_file_name)

    print("copying ./build/teal_fmu-v5-mk1_default/teal_fmu-v5-mk1.bin to ./build/teal_fmu-v5-mk1_default/{}".format(dest_file_name))
    ctx.run("cp ./build/teal_fmu-v5-mk1_default/teal_fmu-v5-mk1.bin ./build/teal_fmu-v5-mk1_default/{}".format(dest_file_name))

    if move_to_images:
        cmd = "cp ./build/teal_fmu-v5-mk1_default/{} /home/mattmc/MattMcFadden/3-Resources/px4-images/{}".format(dest_file_name, dest_file_name)
        ctx.run(cmd)
        #print("cp ./build/teal_fmu-v5-mk1_default/{} /home/mattmc/MattMcFadden/3-Resources/px4-images/{}".format(dest_file_name, dest_file_name))
        print(cmd)

@task
def px4_release(ctx):
    """Step through process for releasing a px4 image to teal-mk1-build"""
    # 1.


@task
def help(ctx):
    """
    invoke --list, plus other stuff
    """
    ctx.run("inv --list")
    print("Notes:")
    print("  source <(invoke --print-completion-script bash)")
    print("  cmd help: inv -h <command>")


@task
def create_project(ctx, project):
    """
    Create my standard project directory structure.
    """
    ctx.run("mkdir {}".format(project))
    ctx.run("mkdir {}/data".format(project))
    ctx.run("mkdir {}/notes".format(project))
    ctx.run("mkdir {}/code".format(project))
    ctx.run("echo \# Project {} Notes, Data, and Code  >> {}/README.md".format(project, project))

@task
def adb_push_logger_conf(ctx):
    """
    Replace the logger.conf file. Some tests currently corrupt it.
    """
    print("Waiting for ADB connection...")
    ctx.run("adb wait-for-device")

    print("Current listing:")
    ctx.run("adb shell ls -l /data/teal/mavlink-router/")
    print("Updating logger.conf...")
    ctx.run("adb push ~/code/teal-mk1-build/meta-teal-core/recipes-teal-log-handler/files/logger.conf /data/teal/mavlink-router/")

    print("New listing:")
    ctx.run("adb shell ls -l /data/teal/mavlink-router/")

@task
def adb_download_drone(ctx):
    """
    Use ADB to download all logs and images from a MK1 drone.
    """

    print("Waiting for ADB connection...")
    ctx.run("adb wait-for-device")
    print("Downloading log files")
    ctx.run("adb pull /data/teal/flight-logs/")
    print("Downloading SDCard")
    ctx.run("adb pull /mnt/sdcard/")

@task
def adb_download_and_wipe_drone(ctx):
    """
    Use ADB to downlaod and delete all logs and images from a MK1 drone.
    """

    print("Waiting for ADB connection...")
    ctx.run("adb wait-for-device")
    print("Downloading log files")
    ctx.run("adb pull /data/teal/flight-logs/")
    print("Downloading SDCard")
    ctx.run("adb pull /mnt/sdcard/")
    adb_wipe_drone(ctx)
    print("Check Drone:")
    ctx.run("adb shell ls -l /data/teal/flight-logs")
    print("Check Download:")
    ctx.run("tree -s")

@task
def adb_wipe_drone(ctx):
    """
    Use ADB to delete all logs and images from a MK1 drone.
    """

    print("Waiting for ADB connection...")
    ctx.run("adb wait-for-device")
    print("Deleting log files")
    ctx.run("adb shell 'rm /data/teal/flight-logs/*'")
    print("Deleting SDCard")
    ctx.run("adb shell 'rm /mnt/sdcard/*'")
    ctx.run("adb shell 'sync'")


@task
def adb_replace_fmu(ctx, image_file):
    """
    Use ADB to update the FMU only. Pushes a new image and calls tealflasher.sh fmu.
    """

    IMAGE_DIR = "/usr/local/tealflasher/images"
    SCRIPT_DIR = "/usr/local/tealflasher"

    print("Waiting for ADB connection...")
    ctx.run("adb wait-for-device")
    print("Removing old PX4 image")
    ctx.run("adb shell rm {}/teal_fmu-v5-mk1_*\.bin".format(IMAGE_DIR))
    print("Copying {} to drone".format(image_file))
    ctx.run("adb push {} {}".format(image_file, IMAGE_DIR))
    print("Programming FMU image")
    ctx.run("adb shell {}/tealflasher.sh fmu".format(SCRIPT_DIR))


@task
def adb_upload_fmu(ctx, image_file, adb_sn=""):
    """
    Using an ADB connection, rename current version of FMU image to something the script won't recognize,
    upload new version.

    Args:
        ctx (invoke context): Invoke Context
        image_file (string): new image file name
        adb_sn (string): optional adb device serial number

    Returns:
        nothing
    """

    IMAGE_DIR = "/usr/local/tealflasher/images"
    SCRIPT_DIR = "/usr/local/tealflasher"

    print("Waiting for ADB connection...")
    ctx.run("adb wait-for-device")

    child = _spawn_adb_shell(ctx, adb_sn)
    child.sendline("cd {}".format(IMAGE_DIR))
    _wait_for_prompt_adb_shell(ctx, child)
    child.sendline('for x in teal_fmu*bin; do mv "$x" _"$x"; done')
    _wait_for_prompt_adb_shell(ctx, child)
    ctx.run("adb push {} {}/".format(image_file, IMAGE_DIR))
    child.sendline('ls -l')
    child.sendline('cd ..')
    child.send('./tealflasher.sh fmu')
    child.interact()

@task
def mav_shell(ctx, ip_address="192.168.1.222"):
    """
    call the python mavlink-shell.py script
    """

    child = pexpect.spawn("/home/mattmc/util/mavlink_shell.py tcp:192.168.1.222:5760")
    child.interact()


@task
def ssh_upload_fmu(ctx, image_file, ip_address="192.168.1.222" ):
    """
    Via an SSH connection, rename current version of FMU image to something the script won't recognize,
    upload new version.

    inv ssh-upload-fmu -i="192.168.1.222" teal_fmu-v5-mk1.bin
    inv ssh-upload-fum teal_fmu-v5-mk1.bin

    Args:
        ctx (invoke context): Invoke Context
        ip_address          : IP of drone
        image_file (string) : new image file name


    Returns:
        nothing
    """

    if not os.path.isfile(image_file):
        print("File \"{}\" not found.".format(image_file))
        sys.exit(1)


    IMAGE_DIR = "/usr/local/tealflasher/images"
    SCRIPT_DIR = "/usr/local/tealflasher"

    print('spawning shell')
    child = _ssh_shell(ctx, ip_address)

    #child = _spawn_adb_shell(ctx, adb_sn)
    print("cd to dir")
    child.sendline("cd {}".format(IMAGE_DIR))
    print("wait for prompt")
    _wait_for_prompt_via_expect(ctx, child)
    print("rename existing image")
    child.sendline('for x in teal_fmu*bin; do mv "$x" _"$x"; done')
    print("wait for prompt")
    _wait_for_prompt_via_expect(ctx, child)
    print("scp new image")
    _scp(ctx, image_file, IMAGE_DIR, ip_address)
    #ctx.run("adb push {} {}/".format(image_file, IMAGE_DIR))
    #ctx.run("scp -i ~/.ssh/mk1-ssh-dev {} root@{}/".format(image_file, IMAGE_DIR))
    child.sendline('ls -l')
    child.sendline('cd ..')
    child.send('./tealflasher.sh fmu')
    child.interact()

@task
def adb_gimbal_stop_shell(ctx, s=""):
    """
    Stop gimbal service before adb shell
    """

    child = _spawn_adb_shell(ctx, s)
    child.sendline("systemctl stop teal-gimbal-conman")
    child.interact()



@task
def adb_update_gimbal_fw(ctx, image_file):
    """
    Use ADB and the tealflasher script to update the gimbal firmware (only).
    Pushes a new image and calls tealflasher.sh
    """

    IMAGE_DIR = "/usr/local/tealflasher/images"
    SCRIPT_DIR = "/usr/local/tealflasher"

    print("Waiting for ADB connection...")
    ctx.run("adb wait-for-device")
    print("Removing old gimbal FW image")
    ctx.run("adb shell rm {}/teal_gimbal_*\.bin".format(IMAGE_DIR))
    print("Copying {} to drone".format(image_file))
    ctx.run("adb push {} {}".format(image_file, IMAGE_DIR))
    print("Programming gimbal image")
    ctx.run("adb shell {}/tealflasher.sh gimbal".format(SCRIPT_DIR))


@task
def adb_pairing_manager_disable(ctx):
    """
    ADB to systemctl restart pairing-manager.
    """
    ctx.run("adb wait-for-device && adb shell systemctl stop pairing-manager && adb shell systemctl disable pairing-manager")

@task
def adb_pairing_manager_enable(ctx):
    """
    ADB to systemclt enable and start pairing-manager
    """
    ctx.run("adb wait-for-device && adb shell systemctl enable pairing-manager && adb shell systemctl start pairing-manager")

@task
def adb_dcm_disable(ctx):
    """
    ADB to stop and disable DCM.
    """
    ctx.run("adb wait-for-device && adb shell systemctl stop dcm && adb shell systemctl disable dcm")

@task
def adb_dcm_enable(ctx):
    """
    ADB to enable and start DCM.
    """
    ctx.run("adb wait-for-device && adb shell systemctl enable dcm && adb shell systemctl start dcm")

@task
def adb_comment_out_qgc_endpoint(ctx):
    """
    Comment out (disable) mavlink-router main.conf QGC Endpoint.
    """
    ctx.run("adb wait-for-device")
    ctx.run("adb shell {}".format(sed_comment_qgc_endpoint))

@task
def adb_uncomment_out_qgc_endpoint(ctx):
    """
    Uncomment (enable) mavlink-router main.conf QGC Endpoint.
    """
    ctx.run("adb wait-for-device")
    ctx.run("adb shell {}".format(sed_uncomment_qgc_endpoint))

@task
def ssh_comment_out_qgc_endpoint(ctx, ip_address='192.168.1.222'):
    """
    SSH comment out (disable) mavlink-router main.conf QGC Endpoint.
    """
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, port = 22, username = 'root', password = 'oelinux123') #connect to drone
    ssh.exec_command(sed_comment_qgc_endpoint)
    ssh.close()

@task
def ssh_uncomment_out_qgc_endpoint(ctx, ip_address='192.168.1.222'):
    """
    SSH uncomment (enable) mavlink-router main.confg QGC Endpoint.
    """
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, port = 22, username = 'root', password = 'oelinux123') #connect to drone
    ssh.exec_command(sed_uncomment_qgc_endpoint)
    ssh.close()

@task
def ssh_log_while_armed(ctx, ip_address='192.168.1.222'):
    """
    SSH change logging to while armed
    """
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, port = 22, username = 'root', password = 'oelinux123') #connect to drone
    ssh.exec_command(sed_comment_log_always)
    ssh.exec_command(sed_uncomment_log_while_armed)
    ssh.close()

@task
def ssh_log_always(ctx, ip_address='192.168.1.222'):
    """
    SSH change logging to always
    """
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, port = 22, username = 'root', password = 'oelinux123') #connect to drone
    ssh.exec_command(sed_uncomment_log_always)
    ssh.exec_command(sed_comment_log_while_armed)

    ssh.close()

@task
def adb_log_while_armed(ctx):
    """
    ADB change logging to while armed
    """

    ctx.run("adb wait-for-device")
    always = "adb shell {}".format(sed_comment_log_always)
    armed  = "adb shell {}".format(sed_uncomment_log_while_armed)
    ctx.run(always)
    ctx.run(armed)


@task
def adb_log_always(ctx, s=""):
    """
    ADB change logging to always
    """

    ctx.run("adb wait-for-device")
    always = "adb shell {}".format(sed_uncomment_log_always)
    armed  = "adb shell {}".format(sed_comment_log_while_armed)
    ctx.run(always)
    ctx.run(armed)


@task
def adb_show_version_file(ctx):
    """
    ADB to cat /etc/versionfile
    """
    print("Waiting for ADB connection...")
    ctx.run("adb wait-for-device")
    ctx.run("adb shell cat /etc/versionfile")

@task
def adb_push_drone_profile(ctx):
    """
    ADB to push ~/util/drone_profile
    """
    ctx.run("adb wait-for-device")
    ctx.run("adb push ~/util/drone_profile /")

@task
def adb_shell(ctx, s=""):
    """
    ADB shell.
    """

    child = _spawn_adb_shell(ctx, s)
    child.interact()

@task
def adb_gimbal_stop_shell(ctx, s=""):
    """
    Stop gimbal service before adb shell
    """

    child = _spawn_adb_shell(ctx, s)
    child.sendline("systemctl stop teal-gimbal-conman")
    child.interact()


@task
def adb_gimbal_stop_run_util(ctx, s=""):
    """
    Stop gimbal service before adb shell
    """

    child = _spawn_adb_shell(ctx, s)
    child.sendline("systemctl stop teal-gimbal-conman && teal_gimbal_util /dev/ttyHS5")

    child.interact()

@task
def adb_gimbal_util(ctx, s=""):
    """
    Run gimbal util from /home/root
    """
    child = _spawn_adb_shell(ctx, s)
    child.sendline("teal_gimbal_util /dev/ttyHS5")

    child.interact()

@task
def adb_gimbal_screen(ctx, s=""):
    """
    Run screen /dev/ttyHS5 460800 to connect to the gimbal uart.
    """
    child = _spawn_adb_shell(ctx, s)

    child.sendline("screen /dev/ttyHS5 460800")

    child.interact()



def _scp(ctx, src_file_path, target_file_path, ip_address="192.168.1.222"):
    print("src:", src_file_path)
    print("trg:", target_file_path)
    print("ip:", ip_address)

    print("sending scp cmd")
    child = pexpect.spawn("scp -i ~/.ssh/mk1-ssh-dev {} root@{}:{} ".format(src_file_path, ip_address, target_file_path))

    while True:
        response = child.expect([pexpect.TIMEOUT, pexpect.EOF, '[#$]'])
        print("==> got response:", response, child.before, child.after)


        if response == 0:
            #for a in child.before:
            #    print(a + "\n")

            return None
        elif response == 1:
            return None
        elif response == 2: #prompt
            return child

def _ssh_shell(ctx, ip_address="192.168.1.222"):
    """
    SSH Shell.
    """

    # clear any existing key to facilitate quickly moving from device to device,
    # or same device with new keys
    #print("Clearing existing SSH keys for {}".format(ip_address))
    #ssh_clearkey = 'ssh-keygen -f "' + os.path.expanduser("~") + '/.ssh/known_hosts" -R ' + ip_address + ' &>/dev/null'
    #os.system(ssh_clearkey)

    new_key = 'Are you sure you want to continue connecting'
    host_id_changed = 'HOST IDENTIFICATION HAS CHANGED'
    ssh_keygen = 'ssh-keygen -f "/home/mattmc/.ssh/known_hosts" -R "192.168.1.222"'
    child = pexpect.spawn("ssh root@{} -i /home/mattmc/.ssh/mk1-ssh-dev".format(ip_address))
    x = 0
    while True:
        response = child.expect([pexpect.TIMEOUT, pexpect.EOF, '[#$]', new_key, 'password:', host_id_changed])
        #print("==> got response:", response)

        if response == 0:
            #print("-->got timeout.")
            return None
        elif response == 1:
            print("EOF detected")
            break
        elif response == 2: #prompt
            #print("-->got prompt")
            #_send_alias_commands(child)
            print(child.before.decode() + child.after.decode(), end='')
            break
        elif response == 3: # new key
            #print("-->got new key")
            print(child.before, child.after)
            child.sendline('yes')
#            time.sleep(0.1)
            time.sleep(1)
        elif response == 4: # password
            #print("-->got password")
            child.sendline("oelinux123")
            #resp = child.expect([pexpect.TIMEOUT, '[#$]'])
        elif response == 5: # host id changed
            #print("-->got HOST CHANGED in _ssh_shell")
            print(child.before, child.after)
            print("sending ssh-keygen")
            ssh_clear_keys(ctx, ip_address)
            child = pexpect.spawn("ssh root@{} -i /home/mattmc/.ssh/mk1-ssh-dev".format(ip_address))
        else:
            break

    return child

@task(help={'ip_address':"IP address of drone"})
def ssh_shell(ctx, ip_address="192.168.1.222"):

    child = _ssh_shell(ctx, ip_address)
    _send_alias_commands(child)
    _set_stty(child)
    child.interact()

@task
def ssh_enable_adb(ctx, ip_address='192.168.1.222'):
    """
    SSH with mk1-ssh-dev key, enable adb
    """
    child = _ssh_shell(ctx, ip_address)
    print("sending {}".format(sed_enable_start_adbd))
    child.sendline(sed_enable_start_adbd)
    while True:
        i = child.expect([pexpect.TIMEOUT, pexpect.EOF, '[#$]', 'fingerprint'])
        if i == 0:
            print(child.before, child.after)
            return None
        elif i == 1:
            print("EOF")
            break
        elif i == 2: #prompt
            print("PROMPT")
            child.sendline()
            command_list = "alias ls=\'ls -F\'; alias ll='ls -l'; alias systemctl='systemctl --no-pager'; cd /data/teal; alias pst='ps | grep teal'"
            child.sendline(command_list)
            break
        elif i == 3: # fingerprint
            print("got fingerprint request")
            print(child.before, child.after)
            child.sendline("yes")
            break
        else:
            print(child.before, child.after)
            break


@task
def ssh_disable_adb(ctx, ip_address='192.168.1.222'):
    """
    SSH with mk1-ssh-dev key, enable adb
    """
    child = _ssh_shell(ctx, ip_address)
    print("sending {}".format(sed_disable_start_adbd))
    child.sendline(sed_disable_start_adbd)
    while True:
        i = child.expect([pexpect.TIMEOUT, pexpect.EOF, '[#$]', 'fingerprint'])
        if i == 0:
            print(child.before, child.after)
            return None
        elif i == 1:
            print("EOF")
            break
        elif i == 2: #prompt
            print("PROMPT")
            break
        elif i == 3: # fingerprint
            print("got fingerprint request")
            print(child.before, child.after)
            child.sendline("yes")
            break
        else:
            print(child.before, child.after)
            break

@task
def adb_radio_telnet(ctx):
    """
    ADB shell telnet to radio
    """
    ctx.run("adb wait-for-device")
    child = pexpect.spawn("adb shell 'telnet 192.168.168.1'")
    while True:
        response = child.expect([pexpect.TIMEOUT, 'login:', 'assword:', '[#$>]'])
        if response == 0:
            print(child.before, child.after)
            return None
        elif response == 1:
            child.sendline("admin")
        elif response == 2:
            child.sendline("teamteal")
        elif response == 3:
            child.sendline("at+mwstatus")
            break
        else:
            print("What?")
            print(child.before, child.after)
            break;

    child.interact()

@task
def adb_push_conman(ctx):
    """
    Push gimbal conman and util to bin after rename
    """

    ctx.run("adb wait-for-device")

    # stop conman
    ctx.run("adb shell systemctl stop teal-gimbal-conman")
    ctx.run("adb shell systemctl --no-pager status teal-gimbal-conman")

    # archive current versions

    # copy new versions into bin dir
    ctx.run("adb push ./teal_gimbal_conman /usr/bin/")
    ctx.run("adb push ./teal_gimbal_util /usr/bin/")

@task
def adb_watch_radio(ctx, s="", ip_of_radio='192.168.168.1'):
    """
    ADB to loop on AT+MWSTATUS
    """

    while True:
#        print("Wait for adb")

        cmd = add_adb_serial_number_param("wait-for-device", s)
        ctx.run(cmd)
        tcmd = "telnet {}".format(ip_of_radio)
        cmd = add_adb_serial_number_param("shell " + tcmd, s)
        child = pexpect.spawn(cmd)
        if child is None:
            print("Child is None")
            time.sleep(5)
        else:
            if watch_radio(child) is not None:
                break

#
#
#
@task
def adb_radio_status(ctx, ip_of_radio='192.168.168.1'):

    print_radio_status("STATUS", "Starting", False)
    while True:
        print_radio_status("STATUS", "Wait For ADB")
        (status, result) = get_radio_status(ctx, 'START')
        if status:
            print_radio_status('STATUS', result)
        else:
            print_radio_status("STATUS", result)
            break
        result = get_radio_status(ctx, "CONNECT")

        while True:
            result = get_radio_status(ctx, "READ")
            if result:
                print_radio_status("MAIN", result, False)

@task
def ip_watch_radio(ctx, ip_of_radio='192.168.168.2'):
    """
    telnet to loop on AT+MWSTATUS
    """
    child = None
    while child is None:
        child = pexpect.spawn("telnet {}".format(ip_of_radio))
        if child is None:
            time.sleep(5)
    watch_radio(child)

@task
def ip_set_radio(ctx, ip_of_radio='192.168.168.2', channel=12):
    """
    telnet to radio, and configure it
    """
    child = None
    while child is None:
        child = pexpect.spawn("telnet {}".format(ip_of_radio))
        if child is None:
            time.sleep(5)

    set_radio(child, str(channel), 'master')

@task
def adb_set_radio_defaults(ctx, ip_of_radio='192.168.168.1', channel=12):
    """
    ADB to set radio and config it
    """
    ctx.run("adb wait-for-device")
    child = None
    #while child is None:
    while True:
        #child = pexpect.spawn("adb shell 'telnet 192.168.168.1'")
        child = pexpect.spawn("adb shell 'telnet {}'".format(ip_of_radio))
        if child is None:
            print("Child is None")
            time.sleep(5)
        else:
            result = set_radio(child, str(channel), 'slave')
            print("result:", result)
            if result is not None:
                break
@task
def adb_radio_off(ctx, ip_of_radio='192.168.168.1'):
    """
    ADB to turn radio off
    """
    ctx.run("adb wait-for-device")
    child = None
    tries = 5;
    while True:
        #child = pexpect.spawn("adb shell 'telnet 192.168.168.1'")
        child = pexpect.spawn("adb shell 'telnet {}'".format(ip_of_radio))
        if child is None:
            print("Child is None")
            tries -= 1
            if tries == 0:
                print("Failed after 5 attempts")
                return
            time.sleep(5)
        else:
            break

    while True:
        response = child.expect([pexpect.TIMEOUT, pexpect.exceptions.EOF,
                                 'login:', 'assword:', '[#$>]', 'Unable to connect',
                                 'OK'])
        if response == 0: # time out
            print("Timeout error")
            print(child.before, child.after)
            return None
        elif response == 1: # EOF Execption
            print("EOF Error connecting. Retrying...")
            time.sleep(5)
            print("returning None")
            return None
        elif response == 2: # log in
            child.sendline("admin")
        elif response == 3: # password
            child.sendline("teamteal")
            #child.sendline("password")
        elif response == 4: # Prompt
            child.sendline("AT+MWRADIO=0")
        elif response == 5: # Unable to connect
            print("Connect error connecting. Retrying...")
            time.sleep(5)
            return None
        elif response == 6: # OK after radio off
            break;
        else:
            print("What?")
            print(child.before, child.after)
            break

    child.sendline("AT&W")
    while True:
        response = child.expect([pexpect.TIMEOUT, pexpect.exceptions.EOF, '[#$>]', 'OK', 'Invalid command'])
        if response == 2:
            continue
        elif response == 3:
            print("OK")
            break



@task
def adb_cmd(ctx, cmds):
    """
    ADB shell <cmds>
    """
    ctx.run("adb wait-for-device")
    ctx.run("adb shell {}".format(cmds))


@task
def ssh_reset_mavlink_router(ctx, ip_address='192.168.1.222'):
    """
    SSH systemctl restart mavlink-router.
    """
    child = _ssh_shell(ctx, ip_address)
    child.sendline('systemctl restart mavlink-router')
    _wait_for_prompt_via_expect(ctx, child)

#    import paramiko
#    ssh = paramiko.SSHClient()
#    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#    ssh.connect(ip_address, port = 22, username = 'root', password = 'oelinux123') #connect to drone
#    ssh.exec_command('systemctl restart mavlink-router')
#    ssh.close()

@task
def ssh_clear_keys(ctx, host='192.168.1.222'):
    """
    Remove SSH known_hosts entry for IP address.
    """
#    ssh_clearkey = 'ssh-keygen -f "' + os.path.expanduser("~") + \
#        '/.ssh/known_hosts" -R ' + host + ' &>/dev/null'

    ssh_clearkey = 'ssh-keygen -f "' + os.path.expanduser("~") + \
        '/.ssh/known_hosts" -R ' + host

    # clear any existing key to facilitate quickly moving from device to device,
    # or same device with new keys
    #os.system(ssh_clearkey)
    ctx.run(ssh_clearkey)

@task(help={'new_image_path': 'Path to new image', 'project_root_dir':'Path to project root directory'})
def teal_mk1_build_update_px4(ctx, new_image_path, project_root_dir = "."):
    """
    Update bitbake with new FMU image.
    inv teal-mk1-build-update-px4 <new_image_path> <project_root>

    """
    # Create Release PX4 image
    # 1.
    #
    # Create teal-mk1-build image
    # 1. create working branch
    # 2. in teal-mk1-build directory,
    #    inv teal-mk1-build-update-px4 ~/reference/images/teal_fmu-v5-mk1_1.9.9.bin
    # 3.
    #


    IMAGE_PATH = project_root_dir + "/meta-teal-core/recipes-tealflasher/files/images/"
    IMAGE_FILE_NAME = os.path.basename(new_image_path)
    TEALFLASHER_BB_PATH = project_root_dir + "/meta-teal-core/recipes-tealflasher/tealflasher.bb"

    if not os.path.isfile(new_image_path):
        print("File \"{}\" not found.".format(new_image_path))
        sys.exit(1)

    if not os.path.isdir(project_root_dir):
        print("Project dir \"{}\" not found.".format(project_root_dir))
        sys.exit(1)

    if not os.path.isfile(TEALFLASHER_BB_PATH):
        print("TEALFLASHER_BB_PATH \"{}\" not found.".format(TEALFLASHER_BB_PATH))
        sys.exit(1)

    old_image_file = get_current_image_file(IMAGE_PATH)
    new_image_destination_path = IMAGE_PATH + IMAGE_FILE_NAME
    print("Replacing {} with {}".format(old_image_file, new_image_destination_path))

    print("git rm {}".format(IMAGE_PATH + old_image_file))
    ctx.run("git rm {}".format(IMAGE_PATH + old_image_file))
    print("cp {} {}/meta-teal-core/recipes-tealflasher/files/images/".format(new_image_path, project_root_dir))
    ctx.run("cp {} {}/meta-teal-core/recipes-tealflasher/files/images/".format(new_image_path, project_root_dir))
    print("git add {}".format(new_image_destination_path))
    ctx.run("git add {}".format(new_image_destination_path))

#    new_file_line = ""
#    new_file_lines = ""
#    file = open(TEALFLASHER_BB_PATH, "r+")
#    for line in file:
#        if "teal_fmu-v5-mk1_" in line:
#            line = line.replace(old_image_file, IMAGE_FILE_NAME)
#
#        new_file_lines = new_file_lines + line
#    file.close()
    new_file_lines = replace_image_name(old_image_file, IMAGE_FILE_NAME, TEALFLASHER_BB_PATH)
    #print("GOT:", new_file_lines)

    new_file = open(TEALFLASHER_BB_PATH+"NEW", "w")
    new_file.write(new_file_lines)
    new_file.close()
    os.rename(TEALFLASHER_BB_PATH, TEALFLASHER_BB_PATH+"OLD")
    os.rename(TEALFLASHER_BB_PATH+"NEW", TEALFLASHER_BB_PATH)
    print("git add {}".format(TEALFLASHER_BB_PATH))
    ctx.run("git add {}".format(TEALFLASHER_BB_PATH))

#
# Helpers, to keep my code clean
#
def get_current_image_file(full_image_path):
    print("image_path:", full_image_path)
    for file in os.listdir(full_image_path):
        if file.startswith("teal_fmu-v5-mk1_"):
            return file

    return None

def replace_image_name(old_image_file, new_image_file_name, bb_file):
    print("1:", old_image_file)
    print("2:", new_image_file_name)
    print("3:", bb_file)

    file = open(bb_file, "r+")
    new_file_lines = ""
    for line in file:
        if "teal_fmu-v5-mk1_" in line:
            line = line.replace(old_image_file, new_image_file_name)

        new_file_lines = new_file_lines + line
    file.close()
    return new_file_lines

def print_if_present(field, text, instance = 1):
    lines = text.split("\n")
    for line in lines:
        if field in line:
            instance -= 1
            if instance > 0:
                continue
            pos = line.find(":") + 1
            print("  " + field.ljust(20) + ":" + line[pos:])
            return

    print("  " + field.ljust(20) + ":" + " "*20)
    return

def print_status(out):
    print("General Status")
    print_if_present("MAC Address", out)
    print_if_present("Operation Mode", out)
    print_if_present("Network ID", out)
    print_if_present("Bandwidth", out)
    print_if_present("Frequency", out)
    print_if_present("Tx Power", out)
    print_if_present("Encryption Type", out)
    print("Traffic Status")
    print_if_present("Receive Bytes", out)
    print_if_present("Receive Packets", out)
    print_if_present("Transmit Bytes", out)
    print_if_present("Transmit Packets", out)
    print("Connection Info")
    print_if_present("MAC Address", out, 2)
    print_if_present("Tx Mod", out)
    print_if_present("Rx Mod", out)
    print_if_present("SNR (dB)", out)
    print_if_present("RSSI (dBm)", out)
    print_if_present("Noise Floor (dBm)", out)

    return

def radio_telnet(child):
    loop_count = 0
    while True:
        response = child.expect(['login:', 'assword:', '[#$>]', 'OK', pexpect.TIMEOUT,
                                 'Unable to connect', pexpect.exceptions.EOF, "Network is unreachable"],
                                 timeout=5)
        if response == 0: # log in
            child.sendline("admin")
        elif response == 1: # password
            child.sendline("teamteal")
        elif response == 2: # Prompt
            child.sendline("at+mwstatus")
        elif response == 3: # OK
            return child
        elif response == 4: # TIMEOUT
            print("Timeout error")
            print(child.before, child.after)
            break
        elif response == 5: # Unable to connect
            print("Connect error connecting. Retrying...")
            child.sendline("")
        elif response == 6: # EOF Execption
            print("EOF Error connecting. Retrying... :", loop_count)
            loop_count += 1
            #print("\033[2A") # up 2 lines
            print(child.before, child.after)
            break
        elif response == 7: #Network unreachable
            print("Network Unreachable")
            return None
        else:
            print("What?")
            print(child.before, child.after)
            return None

    return child


def watch_radio2(child):
    loop_count = 1
    first_display = True

    child = radio_telnet(child)
    if child == None:
        print("Telnet failed")
        return None

    while True:
        response = child.expect(['[#$>]', 'OK', pexpect.TIMEOUT,
                                 'Unable to connect', pexpect.exceptions.EOF],
                                 timeout=5)
        if response == 0:
            child.sendline("AT+MWSTATUS")
        elif response == 1:
            child.sendline("AT+MWSTATUS")
        elif response == 2: # timeout
            print("Timeout Error")
            return None
        elif response == 3:
            print("Lost connection")
            return None
        elif response == 4: # EOF
            print("EOF")
            loop_cout += 1
        else:
            print("What?")
            print(child.before, child.after)
            return None

#    while True:
#        response = child.expect(['login:', 'assword:', '[#$>]', 'OK', pexpect.TIMEOUT,
#                                 'Unable to connect', pexpect.exceptions.EOF, "Network is unreachable"],
#                                 timeout=5)
#        if response == 0: # log in
#            child.sendline("admin")
#        elif response == 1: # password
#            child.sendline("teamteal")
#        elif response == 2: # Prompt
#            child.sendline("at+mwstatus")
#        elif response == 3: # OK
#            if first_display:
#                first_display = False
#            else:
#                print("\033[{}A".format(22))
#
#            out = child.before.decode('UTF-8')
#            print_status(out)
#
#            print("loop count: {}".format(loop_count))
#            loop_count += 1
#            time.sleep(2)
#
#            child.sendline("at+mwstatus")
#            child.expect(r'.+')
#        elif response == 4: # TIMEOUT
#            print("Timeout error")
#            print(child.before, child.after)
#            return None
#        elif response == 5: # Unable to connect
#            print("Connect error connecting. Retrying...")
#            return None
#        elif response == 6: # EOF Execption
#            print("EOF Error connecting. Retrying... :", loop_count)
#            loop_count += 1
#            #print("\033[2A") # up 2 lines
#            print(child.before, child.after)
#            return None
#        elif response == 7: #Network unreachable
#            print("Network Unreachable")
#            return False
#        else:
#            print("What?")
#            print(child.before, child.after)
#            break
#
#    return child


def watch_radio(child):
    loop_count = 1
    first_display = True

    child = radio_telnet(child)
    if child == None:
        print("Telnet failed")
        return None

    while True:
        response = child.expect(['login:', 'assword:', '[#$>]', 'OK', pexpect.TIMEOUT,
                                 'Unable to connect', pexpect.exceptions.EOF, "Network is unreachable"],
                                 timeout=5)
        if response == 0: # log in
            child.sendline("admin")
        elif response == 1: # password
            child.sendline("teamteal")
        elif response == 2: # Prompt
            child.sendline("at+mwstatus")
        elif response == 3: # OK
            if first_display:
                first_display = False
            else:
                print("\033[{}A".format(22))

            out = child.before.decode('UTF-8')
            print_status(out)

            print("loop count: {}".format(loop_count))
            loop_count += 1
            time.sleep(2)

            child.sendline("at+mwstatus")
            child.expect(r'.+')
        elif response == 4: # TIMEOUT
            print("Timeout error")
            print(child.before, child.after)
            return None
        elif response == 5: # Unable to connect
            print("Connect error connecting. Retrying...")
            return None
        elif response == 6: # EOF Execption
            print("EOF Error connecting. Retrying... :", loop_count)
            loop_count += 1
            #print("\033[2A") # up 2 lines
            print(child.before, child.after)
            return None
        elif response == 7: #Network unreachable
            print("Network Unreachable")
            return False
        else:
            print("What?")
            print(child.before, child.after)
            break

    return child

def set_radio(child, channel, role):
    SLAVE_IP="192.168.168.1"
    MASTER_IP="192.168.168.2"
    PASSWD="teamteal"
    KEY="1234567890"
    NET_ID="TeamTeal"
    PAIRING_BANDWIDTH="0"
    PAIRING_CHANNEL_1800="56"
    #PAIRING_CHANNEL=PAIRING_CHANNEL_1800

    command_list = [
            ["AT+MADISS","1,20097"],
            ["AT+MASNMP","0"],
            ["AT+MASNMPTRAP", "0"],
            ["AT+MFGEN","0,1"],
            ["AT+MFGEN","1,1"],
            ["AT+MFGEN","2,1"],
            ["AT+MFGEN","3,1"],
            ["AT+MFGEN","4,1"],
            ["AT+MFGEN","0,1"],
            ["AT+MFDMZ","0,0"],
            ["AT+MNLANDHCP","lan,0"],
            ["AT+MNLANSTP","lan,0"],
            ["AT+MNLANIGMP","lan,0"],
            ["AT+MNLANDR","lan,1"],
            ["AT+MNLANDNS","lan,1"],
            ["AT+MNWAN","0,1"],
            ["AT+MNWANDR","1"],
            ["AT+MNPORT","0,0"],
            ["AT+MNPORT","1,0"],
            ["AT+MSCNTO","600"],
#            ["AT+MSPWD",PASSWD+","+PASSWD],
#            ["AT+MSMNAM","teal-drone"],
            ["AT+MSNTP","0"],
            ["AT+MSSERVICE","0,0"],
            ["AT+MSSERVICE","1,1"],
            ["AT+MSSERVICE","2,0"],
            ["AT+MSWEBUI","0,80,443"],
            ["AT+MWRADIO","1"],
            ["AT+MWDISTANCE","500"],
            ["AT+MWTXPOWER","7"],
            ["AT+MWVENCRYPT","2,"+KEY],
#            ["AT+MWVENCRYPT","1,"+KEY],
            ["AT+MWNETWORKID",NET_ID],
            ["AT+MWEXTADDR","1"],
            ["AT+MWBAND",PAIRING_BANDWIDTH],
            ["AT+MWVRATE","0"],
 #           ["AT+MWFREQ",channel]
             ["AT+MWFREQ","42"]
#            ["AT+MWFREQ2400","42"] # pairing channel for 2400MHz
#            ["AT+MWFREQ2400","70"] # RF Test working frequency
    ]

    #if role == 'slave':
        #command_list.append(["AT+MWVMODE", "1"])
        #command_list.append(["AT+MNLAN","lan,EDIT,0,"+SLAVE_IP+",255.255.255.0"])
    #else:
        #command_list.append(["AT+MWVMODE", "0"])
        #command_list.append(["AT+MNLAN","lan,EDIT,0,"+MASTER_IP+",255.255.255.0"])

    while True:
        response = child.expect(['login:', 'assword:', '[#$>]', pexpect.TIMEOUT,
                                 'Unable to connect', pexpect.exceptions.EOF])
        if response == 0: # log in
            child.sendline("admin")
        elif response == 1: # password
            child.sendline("teamteal")
            #child.sendline("password")
        elif response == 2: # Prompt
            break
        elif response == 3: # time out
            print("Timeout error")
            print(child.before, child.after)
            return None
        elif response == 4: # Unable to connect
            print("Connect error connecting. Retrying...")
            time.sleep(5)
            return None
        elif response == 5: # EOF Execption
            print("EOF Error connecting. Retrying...")
            time.sleep(5)
            print("returning None")
            return None
        else:
            print("What?")
            print(child.before, child.after)
            break

    for command in command_list:
        print(command[0] + "=" + command[1])
        child.sendline(command[0] + "=" + command[1])
        got_ok = False
        while True:
            response = child.expect([pexpect.TIMEOUT, pexpect.exceptions.EOF, '[#$>]', 'OK', 'Invalid command'])
            if response == 0: # Time out
                print("->Timeout")
                continue
            elif response == 1: # EOF
                print("->EOF")
                continue
            elif response == 2: # Prompt
                if got_ok:
                    break
            elif response == 3: # OK
                got_ok = True
            elif response == 4: #Invalid command
                print("->Invalid Command")
            else:
                print("What?", response)

    print("Writing params")
    child.sendline("AT&W")
    while True:
        response = child.expect([pexpect.TIMEOUT, pexpect.exceptions.EOF, '[#$>]', 'OK', 'Invalid command'])
        if response == 2:
            print("Got prompt")
            break
        elif response == 3:
            print("Got OK")


    #print(child.before)
    #print(child.after)

    print("Done")
    return True

#
#
#
def find_and_return_string(field, text, instance=1):
    lines = text.split("\n")
    for line in lines:
        if field in line:
            instance -= 1
            if instance > 0:
                continue
            pos = line.find(":") + 1
            print("  " + field.ljust(20) + ":" + line[pos:])
            return

    return ("  " + field.ljust(20) + ":" + " "*20)

#
#
#
def get_radio_status(ctx, event):
    if event == "START":
        ctx.run("adb wait-for-device")
        return True, "Ready"
    elif event == "CONNECT":
        #child = pexpect.spawn
        pass
    elif event == "READ":
        pass
    return False, "What?"


#
#
#
def add_adb_serial_number_param(cmd, serial_number=""):
    """
    Update command string with serialnumber parameter
    """

    if len(serial_number) == 0:
        return "adb " + cmd

    return "adb -s {} {}\n".format(serial_number, cmd)

def print_radio_status(event, message_text, position_cursor_before=True):

    if position_cursor_before:
        print("\033[2A") # up 2 lines

    if event == "STATUS":
        print("Status:", message_text + " "*(20-len(message_text)))


#
#
#
def _spawn_adb_shell(ctx, s):
    cmd_str = add_adb_serial_number_param("wait-for-device", s)
    shell_str = add_adb_serial_number_param("shell", s)

    ctx.run(cmd_str)
    child = pexpect.spawn(shell_str)
    while True:
        response = child.expect([pexpect.TIMEOUT, '[#$]'])

        if response == 0:
            print("Time out error")
            return None
        else:
            break

    _send_alias_commands(child)
    _set_stty(child)

    return child

def _set_stty(child):
    term_size = os.get_terminal_size()
    child.sendline("stty rows {} cols {}".format(term_size.lines, term_size.columns))

def _send_alias_commands(child):
    commands = ["alias ls=\'ls -F\'",
                "alias ll='ls -lF'",
                "alias systemctl='systemctl --no-pager'",
                "alias pst='ps | grep teal'",
                "cd /home/root; "
               ]
    for c in commands:
        child.sendline(c)


def _wait_for_prompt_adb_shell(ctx, child):
    while True:
        response = child.expect([pexpect.TIMEOUT, '[#$]'])

        if response == 0:
            print("Time out error")
            return None
        else:
            break

    return child

def _wait_for_prompt_via_expect(ctx, child):
    while True:
        response = child.expect([pexpect.TIMEOUT, '[#$]'])

        if response == 0:
            print("Time out error")
            return None
        else:
            break

    return child



sed_comment_log_always        = "sed -i '5s/^#*/#/' /data/teal/mavlink-router/logger.conf"
sed_comment_log_while_armed   = "sed -i '6s/^#*/#/' /data/teal/mavlink-router/logger.conf"
sed_comment_qgc_endpoint      = "sed -i '34,37s/^#*/#/' /data/teal/mavlink-router/main.conf"
sed_uncomment_log_always      = "sed -i '5s/^#*//' /data/teal/mavlink-router/logger.conf"
sed_uncomment_log_while_armed = "sed -i '6s/^#*//' /data/teal/mavlink-router/logger.conf"
sed_uncomment_qgc_endpoint    = "sed -i '34,37s/^#*//' /data/teal/mavlink-router/main.conf"
sed_enable_start_adbd         = "sed -i 's/^START_ADBD=0/START_ADBD=1/' /etc/default/adbd"
sed_disable_start_adbd        = "sed -i 's/^START_ADBD=1/START_ADBD=0/' /etc/default/adbd"
