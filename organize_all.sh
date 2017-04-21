#!/bin/bash

IMHERE="$(dirname "$0")"
. "${IMHERE}"/utils.sh

showhelp(){
        echo $0 '<target_dir>'
}
getoption "$1" target_dir "./"

for folder in "$target_dir"/*; do
	if [[ ! -d "$folder" ]]; then
		#echo "skipping $folder since it's not a folder"
		continue;
	fi
	echo "${IMHERE}"/organize.sh "$folder"
	"${IMHERE}"/organize.sh "$folder"
done
