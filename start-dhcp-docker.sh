#!/bin/bash
cd /home/mattmc/util/dhcpd
docker run -it --rm --init --net host -v "$(pwd)/data":/data networkboot/dhcpd enp2s0

