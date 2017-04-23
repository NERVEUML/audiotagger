#!/bin/bash	
# This file has bits of:
#	http://stackoverflow.com/questions/7039130/bash-iterate-over-list-of-files-with-spaces
#	http://stackoverflow.com/questions/3685970/check-if-an-array-contains-a-value
#	http://www.linuxjournal.com/content/return-values-bash-functions
#	http://stackoverflow.com/questions/19111067/regex-match-either-string-in-linux-find-command


IMHERE="$(dirname "$0")"
. ${IMHERE}/common.sh

showhelp(){
	echo $0 'target_dir file_extension_to_work_on workingdir 1_or_0_to_force '
}
getoption "$1" target_dir
getoption "$2" workingdir "." #where to put working files, allows having them separate from the video files
getoption "$3" forceoverwrite 0


find "$target_dir" -type f -regextype posix-extended -iregex "${videofileregex}" -exec \
	"${IMHERE}/tag.sh" '{}' "$forceoverwrite" "$workingdir" \;
