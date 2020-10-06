#!/bin/sh

adb wait-for-device
adb shell systemctl stop usb-gadget
adb shell systemctl disable usb-gadget
