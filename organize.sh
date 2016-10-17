#!/bin/bash

demod(){
	for file in "$@"; do
		ffmpeg -i "$file" "$file".wav
		multimon-ng -c -a AFSK1200 -t wav "$file".wav > "$file".demod
		cat "$file".demod | grep -v AFSK1200 |cut -d " " -f 2 > "$file".tags
	done
}
tag(){
	for file in "$@"; do
		echo
		echo "$file"
		most="$(cat "$file".tags |cut -d ":" -f 1 |sort |uniq -c | sort -nr |head -n 1)"
		if [[ "$most" == "" ]]; then
			echo -e "\tThis does not appear to have any tags."
			continue
		fi
		name="$(echo "$most" |grep -oE '\w+_.+\..+')"
		echo -e "\tMoving $file to $name,\t $most"
		mkdir -p "$name"
		ln -s "$file" "$name"
		ln -s "$file".* "$name"
	done
}
