#!/bin/bash

IMHERE="$(dirname "$0")"
. ${IMHERE}/utils.sh


showhelp(){
        echo $0 '<file_of_filenames>'
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


