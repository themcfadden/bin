#!/usr/bin/env bash

function usage()
{
    cat <<HEREDOC
    Usage: $PROGRAM_NAME [NUM] [--delay NUM] [--help] 
    optional arguments:
             -d, --persist  Run again, until cancel is hit
             -h, --help     Show this help message and exit
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

# Init script vars
PROGRAM_NAME=$(basename $0)
DELAY_PERIOD=60
RUN_UNTIL_CANCEL=0
POSITIONAL=()

while [[ $# -gt 0 ]]
      do
          key="$1"

          case $key in
              -p|--persist)
                  RUN_UNTIL_CANCEL=1
                  shift # past argument
                  #shift # past value
                  ;;
              -h|--help)
                  usage; exit;
                  shift # past argument
                  #shift # past value
                  ;;
              *)
                  POSITIONAL+=("$1")
                  shift # past argument
                  ;;
          esac
done

set -- "${POSITIONAL[@]}" # restore positional params


while true
do
      DELAY_PERIOD=$(zenity --entry --text="Mute Audio Duration" --entry-text=$DELAY_PERIOD)

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

      if [ $RUN_UNTIL_CANCEL -eq 0 ]; then break; fi
done

