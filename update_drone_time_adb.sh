#!/usr/bin/env bash

currentDate=`date --utc +"%Y%m%d"`
currentTime=`date --utc +"%H:%M:%S"`
execString="date +%Y%m%d -s \"$currentDate\"; date +%T -s \"$currentTime\"; ."
echo -e "\nUpdating date & time:"
adb shell "$execString"
echo -e "\nReading back out system time:"
adb shell "date; ."
echo -e "\n"
