#!/bin/bash

IMHERE="$(dirname "$0")"
. "${IMHERE}"/common.sh

getoption "$1" each 
getoption "$2" force 0
getoption "$3" workingdir "." #where to put the working files, allows having them somewhere other than with video files

filext="${each:(-3)}"
#fphash="$(md5sum "$each" | cut -c 1,10)"
fpshort="$(dirname "$each" | tr -d '/:_\-\.' )"
fn="$(basename "$each")"
neweach="$workingdir"/"$fpshort"/"$fn"

if [[ "$filext" == "MOV" ]]; then
	camera="jvc"
elif [[ "$filext" == "MP4" ]]; then
	camera="gopro"
else
	camera="unknown camera"
fi
echo "$each"
echo " is $camera file"

if [[ $force == 1 || ! -f "${neweach}.orig.aprs" ]]; then
	mkdir -p "$workingdir"/"$fpshort"
	echo "$each" | tee "$neweach.oldname"
	if [[ "$camera" == "gopro" ]]; then
		ffmpeg -i "$each" -vn -acodec copy "$neweach.aac" > "$neweach.ffmpeglog1" 2>&1
		ffmpeg -i "$neweach.aac" "$neweach.orig.flac" > "$neweach.ffmpeglog2" 2>&1
	else
		ffmpeg -i "$each" -vn "$neweach".orig.flac > "$neweach.ffmpeglog1" 2>&1
	fi
	"${IMHERE}"/multimon-ng/multimon-ng -c -a AFSK1200 -t flac "$neweach.orig.flac" > "$neweach.orig.aprs"
else
	echo "$each already done"
fi
#grep -ir "team1 1a 2.1" */*/*.aprs |cut -d : -f 1 |xargs -n 1 basename |cut -f 1,2 -d . |sort -u
#for each in *; do echo "$each"; mkdir -p "$each".d; while read line; do echo "$line"; ln -s "$line" "$each".d; done <"$each"; done
#for file in *.d/*; do readlink "$file"; done
#removelink() {
#  [ -L "$1" ] && cp --remove-destination "$(readlink "$1")" "$1"
#}
#for file in *.d/*; do removelink "$file"; done
#sox -q "$neweach.orig.flac" "$neweach.flac" remix 1 0 channels 1 norm
