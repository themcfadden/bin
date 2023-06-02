#!/bin/bash

cd $HOME/util/dhcpd
docker run -it --rm --init --net host -v "$(pwd)/data":/data networkboot/dhcpd enp2s0

