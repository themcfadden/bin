#!/bin/sh
find . -type f -exec grep --color=always -nH --null -e $1 \{\} +