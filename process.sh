#!/bin/bash

IMHERE="$(dirname "$0")"
. "${IMHERE}"/common.sh

showhelp(){
        echo $0 '<target_dir>'
}
getoption "$1" target_dir "./"

for subdir in "$target_dir"/*; do
	if [[ ! -d "$subdir" ]]; then continue; fi
	"${IMHERE}"/tagall.sh "$subdir" 
done
echo "Tagging videos...will return when complete"
jobs -l
wait
for subdir in "$target_dir"/*; do
	if [[ ! -d "$subdir" ]]; then continue; fi
	"${IMHERE}"/organize.sh "$subdir" 
done
echo "Running organization...will return when complete"
jobs -l
wait
for subdir in "$target_dir"/*; do
	if [[ ! -d "$subdir" ]]; then continue; fi
	"${IMHERE}"/cutter.sh "$subdir" 
done
echo "Running ffmpeg cuts...will return when complete"
jobs -l
wait
echo "Completed tagging, organization, and auto-cuts!"
