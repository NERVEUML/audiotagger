#!/bin/bash	
# This file has bits of:
#	http://stackoverflow.com/questions/7039130/bash-iterate-over-list-of-files-with-spaces
#	http://stackoverflow.com/questions/3685970/check-if-an-array-contains-a-value
#	http://www.linuxjournal.com/content/return-values-bash-functions

. utils.sh

showhelp(){
	echo $0 '<target_dir[./,...]> <bitrate[120,1200,...]> <force_overwrite[1,0]>'
}
getoption "$1" target_dir
getoption "$2" bitrate
getoption "$3" filext mp4
getoption "$4" forceoverwrite 0

find "$target_dir" -type f -iname *."$filext" -exec ./tag.sh '{}' "$bitrate" "$forceoverwrite" \;
