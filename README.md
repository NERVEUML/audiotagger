AFSK video tagging
==================

Summary
-------
Synchronizing and organizing (relatively) massive amounts of video
footage of an event (robot testing, in this case) from many consumer cameras
operated by untrained users is labor intensive, and error prone. Editing
together test footage can sometimes take more than 1:1 time for a given piece of
footage (i.e. it can take more than an hour to properly edit an hour of
video, and we may generate hundreds or thousands of hours of video).

Luckily, there exist many great pieces of free and open software that
can help us organize and cut video.

Recorded video will have an audio channel containing AFSK packets
received on the radios - which, by their nature, will be synchronized with
all other cameras recording at that time. These packets will contain
information about the current event they are recording, and a timestamp.

In this way, we can automatically process recorded event footage,
organize it by event, timestamp it with a known-good time and date
regardless of the individual camera's settings, and even cut the
video based on the decoded packets. Each of these features eliminate
processing that was completely human labor in the past, saving time
and money.

Usage
-----

To generate audio tags:

```
./direwolf/direwolf -t 0 -c direwolf/direwolf.conf &
./gentag 15 nerve stairs_45 1.1
```

To extract tags from video files:

```
./tagall.sh foldername
```

To organize and cut video files that have had tags extracted:

```
./organize.sh foldername
./cutter.sh foldername
```

These scripts will run tasks serially without regard to further folder structure (video files are identified by file extension using GNU find).

Need it faster, or more parallel on large video sets? Read on.

We have video that is typically copied into this folder structure:

* 2017.01
	* monday
	* tuesday
	* wednesday
	* thursday
	* friday

So there's an `org_and_cut.sh` which will start parallel jobs for each of the subfolders of the target directory.

```
./org_and_cut.sh 2017.01/
```



Requirements
------------
We use [Direwolf](https://github.com/wb2osz/direwolf) for the TNC,
connected to a Signalink USB (though any form of radio interface would
work). On the decoding and sorting side, we use
[a fork](https://github.com/NERVEUML/multimon-ng) of
[multimon-ng](https://github.com/EliasOenal/multimon-ng), where our fork
outputs offsets into a file being decoded for APRS.

On .deb systems, Direwolf requires the `libasound-dev` package during compilation.

```
virtualenv -p python2 env
source env/bin/activate
pip install -r requirements.txt
pushd ..
git clone https://github.com/ampledata/kiss.git
git clone https://github.com/ampledata/aprs.git 
popd
ln -s ../kiss/kiss
ln -s ../aprs/aprs
```

Then there's a bunch of fragile, hacky code for decoding, organizing,
and cutting video files!

APRS
----
Since it's all APRS packets, there's suddenly a lot of capability
for tagging videos with location, weather, etc. And, since it's still
ultimately an audio track, you can always key up the correct channel with
a walkie talkie and save yourself some verbal notes or comments. We've
found Adobe Premiere likes very much the shared audio channel for
automatic synchronization, if you can't use these scripts but still have
tagged video.  The Premiere synchronization seems to work well even if
the audio doesn't quite come through (say, if you messed up the audio
input settings on all the cameras).


Hints
-----
Tags will be offset from the real world time - you can deal with this by estimating the latency (includes tx of preamble frame flags, etc) and then trying to correct the timestamps sent, or you can deal with it later. Packets are decoded at the end, so the timestamp tag offset is largely the tx preamble, and the length of the packet (around 2.5s for me, for a number of reasons).
The offset can be worse (especially when sending many packets at once), but is largely consistent across many packets.

direwolf.conf
-------------
```
CHANNEL 0
MYCALL ......
DWAIT 0
TXDELAY 75
```


Process
------
```
tagall.sh 
	runs tag.sh on all files of a particular fileextension within a target directory

tag.sh 
	rips the audio from the file into a flac, and then 
		file.mp4 -> file.mp4.orig.flac
	runs the flac past a patched multimon-ng that 
		outputs file offsets during the decoding process.
			file.mp4 -> file.mp4.orig.aprs
organize.sh 
	finds all the .aprs files, 
	`grep AFSK -b1`s them, 
	pipes that output through by_tag.py which 
		parses packets into run data and 
			.aprs -> .runs.json
			.aprs -> .runs
		generates ffmpeg command lines for each run for each video
			.aprs -> runs.ffmpeg
	creates lists of runs in the target directory
	for each run in the list of runs
		creates lists of uncut videos in that run
	calls filelist_to_symlinks.sh which
		converts a list of filenames to symlinks (relies on get_orig_fn in utils.sh)
		
cutter.sh
	finds all the .ffmpeg files (which contain ffmpeg lines to cut videos)
		and runs each command line

org_and_cut.sh
	runs first organize.sh and then cutter.sh on subdirectories of a target directory in parallel

```
