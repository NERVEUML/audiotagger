#!/bin/bash

IMHERE="$(dirname "$0")"
. ${IMHERE}/utils.sh

getoption "$1" each 
getoption "$2" bitrate 1200
getoption "$3" force 0

echo "$each"
filext="${each:(-3)}"

if [[ "$filext" == "MOV" ]]; then
	camera="jvc"
elif [[ "$filext" == "MP4" ]]; then
	camera="gopro"
fi
echo " is $camera file"

if [[ $force == 1 || ! -f "${each}.orig.aprs" ]]; then
	if [[ "$camera" == "gopro" ]]; then
		ffmpeg -i "$each" -vn -acodec copy "$each.aac" > "$each.ffmpeglog1" 2>&1
		ffmpeg -i "$each.aac" "$each.orig.flac" > "$each.ffmpeglog2" 2>&1
	elif [[ "$camera" == "jvc" ]]; then
		ffmpeg -i "$each" -vn "$each".orig.flac > "$each.ffmpeglog1" 2>&1
		#sox -q "$each.orig.flac" "$each.flac" remix 1 0 channels 1 norm
	fi
	multimon-ng -c -a AFSK1200 -t flac "$each.orig.flac" > "$each.orig.aprs"
else
	echo "$each already done"
fi

#old stuff maybe useful later
	#sox -q "$each.ogg" "$each.orig.flac" 
	#sox -q "$each.ogg" "$each.flac" remix 1 0 channels 1 norm
	#sox -q "$each.ogg" "$each.flac" channels 1 norm
	#sox -q "$each.ogg" "$each.wav" 
	#minimodem -r $bitrate --stopbits 3 --startbits 3 -q -f "$each.flac" > "${each}_${bitrate}.txt"
	#minimodem -r $bitrate -q -f "$each.flac" > "${each}_${bitrate}.txt"
	#rm -f "$each.aac" "$each.ogg" "$each.flac" "$each.wav"
