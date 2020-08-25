#!/bin/sh

# Run this, then turn on drone. 
adb wait-for-device
adb shell systemctl stop usb-gadget
adb shell systemctl disable usb-gadget


