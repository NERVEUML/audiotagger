#!/bin/bash

IMHERE="$(dirname "$0")"
. "${IMHERE}"/utils.sh


showhelp(){
        echo $0 '<target_dir>'
}
getoption "$1" target_dir "./"

mkdir -p "$target_dir"/cut
find "$target_dir" -iname "*.$ffmpegext" -exec cat '{}' \; > "$target_dir"/cut/"$ffmpeglist"
pushd "$target_dir"/cut
while read cmd; do
	$cmd </dev/null
done < "$ffmpeglist"
popd
