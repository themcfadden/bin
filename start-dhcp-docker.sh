#!/bin/sh

cd $HOME/bin/dhcpd
docker run -it --rm --init --net host -v "$(pwd)/data":/data networkboot/dhcpd en7

