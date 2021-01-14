#!/usr/bin/env bash

function usage()
{
    cat <<HEREDOC
    Usage: $PROGRAM_NAME [NUM] [--delay NUM] [--help] 
    optional arguments:
             NUM, -d, --delay NUM   Delay NUM seconds
             -h, --help             Show this help message and exit

    If no argument is specified, delay for 30 seconds.
HEREDOC
}

machine=Linux
function read_machine_type()
{
    unameOut="$(uname -s)"
    case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
    esac
    echo ${machine}
}

function os_is()
{
    local n=0
    #if [[ "$1" = "-n" ]]; then n=1;shift; fi

    #echo $OS|grep $1 -i >/dev/null
    uname -s |grep -i "$1" >/dev/null

    return $(( $n ^ $? ))
}


function mute()
{

    os_is Darwin &&
    {
        current_volume=$(osascript -e 'output volume of (get volume settings)')
        osascript -e 'set volume output volume 0' # MacOS
    }

    os_is Linux &&
    {
        amixer -q -D pulse sset Master mute
    }
}

function unmute()
{
    os_is Darwin &&
    {
        osascript -e "set volume output volume $current_volume" # MacOS
    }

    os_is Linux &&
    {
        amixer -q -D pulse sset Master unmute
    }


}

DELAY_PERIOD=60
while true
do
      DELAY_PERIOD=$(zenity --entry --text=Mute Audio --entry-text=$DELAY_PERIOD)

      if [[ -z "$DELAY_PERIOD" ]]; then break; fi

      # Issue our mute command
      mute

      wait_period=0
      while true
      do
          wait_period=$(($wait_period+1))
          if [ $wait_period -gt $DELAY_PERIOD ]; then
              break
          else
              sleep 1
          fi
      done

      # Issue our unmute command
      unmute
done
