#!/bin/bash

IMHERE="$(dirname "$0")"
. "${IMHERE}"/utils.sh

showhelp(){
        echo $0 '<target_dir>'
}
getoption "$1" target_dir "./"

#TODO don't hardcode location of by_tag
find "$target_dir" -type f -iname "*."$aprsfilext"" -exec \
	bash -c "grep AFSK -b1 {} | ~mike/audiotagger/by_tag.py {} {}.runs.json {}.runs.ffmpeg |tee {}.runs " \;

find "$target_dir" -iname "*.$runsfilext" -exec cat '{}' \; |sort  |cut -f 1 -d " " |uniq > "$target_dir"/"$runlist"
while read runname; do
	rundir="$target_dir"/uncut/"$runname"
	mkdir -p "$rundir"
	grep -iRl --include=*."$runsfilext" "$runname" "$target_dir" > "$rundir"/"$videolist"
done < "$target_dir"/"$runlist"

#TODO don't hardcode location of by_tag
find "$target_dir" -iname "$videolist" -exec ~mike/audiotagger/filelist_to_symlinks.sh '{}' \;

#while read run; do rm -r $run; done < runlist.txt
#find ./ -iname "*.runs" -print -exec cat '{}' \;
