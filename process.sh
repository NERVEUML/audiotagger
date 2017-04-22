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
	"${IMHERE}"/tagall.sh "$folder" 2>&1 >> "$folder".tagall_log &
done
echo "Tagging videos...will return when complete"
jobs -l
wait
for folder in "$target_dir"/*; do
	if [[ ! -d "$folder" ]]; then
		#echo "skipping $folder since it's not a folder"
		continue;
	fi
	"${IMHERE}"/organize.sh "$folder" 2>&1 >> "$folder".organization_log &
done
echo "Running organization...will return when complete"
jobs -l
wait
for folder in "$target_dir"/*; do
	if [[ ! -d "$folder" ]]; then
		#echo "skipping $folder since it's not a folder"
		continue;
	fi
	"${IMHERE}"/cutter.sh "$folder" 2>&1 >> "$folder".cutter_log &
done
echo "Running ffmpeg cuts...will return when complete"
jobs -l
wait
echo "Completed tagging, organization, and auto-cuts!"
