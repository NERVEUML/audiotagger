#!/bin/bash	

for each in srcvids/*.mp4; do 
	echo "$each"; 
	ffmpeg -loglevel quiet -i $each -vn -acodec copy "$each".aac
	ffmpeg -loglevel quiet -i $each.aac $each.ogg
	sox -q $each.ogg $each.flac channels 1 norm
	sox -q $each.ogg $each.wav 
	minimodem -r 300 --stopbits 3 --startbits 3 -q -f $each.flac |sort |uniq -c |sort -n |tee $each.txt
	minimodem -r 300 -M 1000 -S 3000 --stopbits 3 --startbits 3 -q -f $each.flac |sort |uniq -c |sort -n |tee -a $each.txt
	rm $each.aac $each.ogg $each.flac
done
