#! /bin/sh

(ifconfig $1 | grep inet | awk '$1=="inet" {print $2}')
