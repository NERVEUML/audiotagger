#!/bin/bash
pipe="fifo1"

if [[ -z $1 ]] ; then
	echo "Group?: "
	read group
else 
	group=$1
fi
if [[ -z $2 ]] ; then
	echo "Task?: "
	read task
else 
	task=$2
fi
if [[ -z $3 ]] ; then
	echo "Run?: "
	read run
else 
	run=$3
fi
timestamp=$(date +%s)
datestamp=$(date)
repeat=1
fileout="nerveafsk.out"
playthis="$fileout.playthis"
#mkfifo $pipe
rm *.fec

msg=""
for (( i=0; i < $repeat; i++ )); do
	msg+="$group T:$task R:$run $timestamp "
done
c=$(echo "$msg" |wc -c)
>$fileout
>$playthis
echo $msg >> $fileout

zfec -m 15 -k 3 $fileout
for fec in $fileout.*_*.fec; do
	b=$(cat $fec | base64)
	echo $b >> $playthis
done

minimodem -t 300 --tx-carrier --stopbits 3.0 --startbits 3.0 < $playthis
