#!/bin/bash

IMHERE="$(dirname "$0")"
. ${IMHERE}/utils.sh


showhelp(){
        echo $0 '<file_of_filenames>'
}
get_orig_fn(){
	getoption "$1" rundata
	#./tags/mntfladata201611unorganizedmondaygopropci000000140usb062210scsi0000part1DCIM100GOPRO/GP010003.MP4.orig.aprs.runs
	#.orig.aprs.runs = 15
	nameholder="${rundata::-15}"
	orig_filename="$(cat "$nameholder".oldname)"
	echo "$orig_filename"
}
hashname(){
	getoption "$1" orig_filename
	hash="$(echo -n "$orig_filename" | md5sum |cut -c 1-10)"
	ext="${orig_filename:(-4)}"
	echo "$hash""$ext"
}
getoption "$1" filelist
targetdir="$(dirname "$filelist")"
while read filename; do
	echo "$filename"
	orig_fn="$(get_orig_fn "$filename")"
	hash="$(hashname "$orig_fn")"
	ln -s "$orig_fn" "$targetdir"/"$hash"
done < "$filelist"


