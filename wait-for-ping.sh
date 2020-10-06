#!/bin/bash

while !(ping -c 1 -t 2 $1 &> /dev/null)
do
    sleep 2
done
