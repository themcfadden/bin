#!/bin/bash

adb forward tcp:12345 tcp:12345
adb shell busybox nc -lp 12345 -e "$@" &
sleep 1s
exec nc -q 1 localhost 12345
