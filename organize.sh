#!/bin/bash

IMHERE="$(dirname "$0")"
. "${IMHERE}"/common.sh

showhelp(){
        echo $0 '<target_dir>'
}
getoption "$1" target_dir "./"

#TODO don't hardcode location of by_tag
find "$target_dir" -type f -iname "*."$aprsfilext"" -exec \
	bash -c "grep AFSK -b1 {} | ~/audiotagger/by_tag.py {} {}.runs.json {}.runs.ffmpeg |tee {}.runs " \;

find "$target_dir" -iname "*.$runsfilext" -exec cat '{}' \; |sort  |cut -f 1 -d " " |uniq > "$target_dir"/"$runlist"
while read runname; do
	rundir="$target_dir"/uncut/"$runname"
	mkdir -p "$rundir"
	grep -iRl --include=*."$runsfilext" "$runname" "$target_dir" > "$rundir"/"$videolist"
done < "$target_dir"/"$runlist"

#list of untagged videos
#TODO add folder of untagged videos
#TODO generic way to take list of files (runs, .aprs, .json, whatever) and make directories with copies of those videos, cut or uncut
# e.g. a way to find all videos tagged as 'crashes', or all untagged videos, etc
find "$target_dir" -iname "*.$runsfilext" -size 0 > "$target_dir"/untagged.txt
#while read filename; do


#TODO don't hardcode location of by_tag
find "$target_dir" -iname "$videolist" -exec ~/audiotagger/filelist_to_symlinks.sh '{}' \;

#while read run; do rm -r $run; done < runlist.txt
#find ./ -iname "*.runs" -print -exec cat '{}' \;


#find all files in a directory
# for each file
