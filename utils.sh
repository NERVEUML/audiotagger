#!/bin/bash
containsElement () {
	local e
	for e in "${@:2}"; do [[ "$e" == "$1" ]] && return 0; done
	return 1
}
getoption(){
	option="$1"
	local  __resultvar=$2
	default="$3"
	if [[ -z "$option" ]]; then
		if [[ -z "$default" ]]; then
			showhelp
			exit
		else 
			option="$default"
		fi
	fi
	if [[ "$__resultvar" ]]; then
		eval $__resultvar="'$option'"
	else
		echo "$option"
	fi

}
get_orig_fn(){
	getoption "$1" rundata
	#./tags/mntfladata201611unorganizedmondaygopropci000000140usb062210scsi0000part1DCIM100GOPRO/GP010003.MP4.orig.aprs.runs
	#.orig.aprs.runs = 15
	nameholder="${rundata::-15}"
	orig_filename="$(cat "$nameholder".oldname)"
	echo "$orig_filename"
}
#for each in *.MP4; do echo "$each"; ffmpeg -i "$each" "$each".flac; done
#for each in *.MP4; do echo "$each"; multimon-ng -c -a AFSK1200 -t flac "$each.flac" > "$each.aprs"; done
#cat *.aprs |grep -i {{T | cut -d " " -f 2-4 |sort -u


#ffmpeg -i input.flv -vf "select='eq(pict_type,PICT_TYPE_I)'" -vsync vfr thumb%04d.png
#ffmpeg -framerate 60 -i thumb%04d.png -c:v libx264 -r 30 -pix_fmt yuv420p thumbs.mp4

#https://trac.ffmpeg.org/wiki/How%20to%20speed%20up%20/%20slow%20down%20a%20video
#https://trac.ffmpeg.org/wiki/Create%20a%20thumbnail%20image%20every%20X%20seconds%20of%20the%20video


#ffmpeg -i input.mp4 -vf "select=gt(scene\,0.003),setpts=N/(25*TB)" output.mp4
#http://superuser.com/questions/984841/ffmpeg-remove-parts-without-motion


