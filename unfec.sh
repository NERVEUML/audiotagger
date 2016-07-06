#!/bin/bash
c=0
while read -r line ; do
	echo $c
	printf '%s' "$line" >> "${c}.seq"
	c=$(($c+1))
done
zunfec *.seq -o nerveafsk.in
