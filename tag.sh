#!/bin/bash

. utils.sh

getoption "$1" each 
getoption "$2" bitrate 1200
getoption "$3" force 0

echo "$each"; 
if [[ $force == 1 || ! -f "${each}_${bitrate}.txt" ]]; then
	ffmpeg -loglevel quiet -i "$each" -vn -acodec copy "$each.aac"
	ffmpeg -loglevel quiet -i "$each.aac" "$each.ogg"
	sox -q "$each.ogg" "$each.flac" channels 1 norm
	sox -q "$each.ogg" "$each.wav"
	minimodem -r $bitrate --stopbits 3 --startbits 3 -q -f "$each.flac" > "${each}_${bitrate}.txt"
	rm -f "$each.aac" "$each.ogg" "$each.flac" "$each.wav"
else
	echo "$each already done"
fi
