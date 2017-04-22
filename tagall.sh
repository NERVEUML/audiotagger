#!/bin/bash	
# This file has bits of:
#	http://stackoverflow.com/questions/7039130/bash-iterate-over-list-of-files-with-spaces
#	http://stackoverflow.com/questions/3685970/check-if-an-array-contains-a-value
#	http://www.linuxjournal.com/content/return-values-bash-functions


IMHERE="$(dirname "$0")"
. ${IMHERE}/utils.sh

showhelp(){
	echo $0 'target_dir file_extension_to_work_on workingdir 1_or_0_to_force '
}
getoption "$1" target_dir
getoption "$2" filext mp4
getoption "$3" workingdir "." #where to put working files, allows having them separate from the video files
getoption "$4" forceoverwrite 0

find "$target_dir" -type f -iname "*."$filext"" -exec \
	"${IMHERE}/tag.sh" '{}' "$forceoverwrite" "$workingdir" \;
