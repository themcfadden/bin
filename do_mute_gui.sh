#!/usr/bin/env sh

function usage()
{
    echo "Usage: $PROGRAM_NAME [NUM] [--delay NUM] [--help]"
    echo "optional arguments:"
    echo "   -d, --persist  Run again, until cancel is hit"
    echo "   -h, --help     Show this help message and exit"
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

modify_win_by_pid() {
    pid=$1

    sleep 0.2
    win_id=`wmctrl -l -p | grep ${pid} | awk '{print $1}'`
    wmctrl -i - ${win_id} -b add,above
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

      # Check that is has a value
      if [[ -z $DELAY_PERIOD ]]; then break; fi
      # Check that the value is a number.
      REGEX="^[0-9]+$"
      if ! [[ $DELAY_PERIOD =~ $REGEX ]];
      then
          break;
      fi

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

