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

The end result takes advantage of the ubiquity of cheap, bubble-pack
FRS radios, low baud-rate AFSK signaling, a packet structure
similar to FX25 (the forward error correction wrapper around AX.25), and
the audio channels of the recording cameras. 

Recorded video will have an audio channel containing AFSK packets
received on the radios - which, by their nature, will be synchronized with
all other cameras recording at that time. These packets will contain
information about the current event they are recording, and a timestamp.

In this way, we can automatically process recorded event footage,
organize it by event, timestamp it with a known-good time and date
regardless of the individual camera's settings, and perhaps even cut the
video based on the decoded packets. Each of these features eliminate
processing that was completely human labor in the past, saving time
and money.


Software
--------

* minimodem: a general-purpose software audio FSK modem
	(Give it bytes, it plays tones over speaker, etc)

* ffmpeg, sox: rip audio from video, convert between audio formats, etc

* python and bash: glue to slap it all together


History
-------

Initial experiments showed 300 baud was reliable enough to get >50%
decode rate by playing the generated audio through 

1. laptop speakers->radio mic
2. over NFM rf
3. back out through a radio speaker->camera mic from some distance away (~1-3 ft),

and still decode - that was without forward error correction, and showed
the idea was workable. Even at 50% decode, it is worth it - every video
it works in, is a video that will require less human processing time.

Further efforts at 300 baud without audio cables resulted in 
70% < decode rates < 80%. Audio cables brings that up to around 95%+
with little effort, and mean we can even use 1200 baud, like common APRS.

The current implementation does 300 and 1200 baud signaling.
We've also replaced the speaker <--> microphone gaps with audio cables
for better quality and replicability. Less fiddling with volume knobs
is a Good Thing. 


Problems and future
-------------------

I've probably made a mess of the packet structure, don't
have enough signals experience to /really/ know what I'm doing; and yet,
it works! We can now automagically pull videos off SD cards, sort them by
project and timestamp, and group them accordingly - based entirely on
the AFSK tags. 

* The current /\/\otorola FRS radios sometimes take as long as five
seconds to break squelch, making them unusable for this, and general
usage.
* Error rate can always be better, and tagging can always be less fragile.
* Moving from FRS to itinerant part 90 frequencies will add flexibility.

Future work involves automatically cutting videos to start at
the timestamp indicated by first decodable packet, and improving error
rates. We're looking into itinerant business freqs, and better radios
(cheap part 90 cert. Baofengs, at least on the listening side).
A proper TNC/modem might require less configuration and
should result in better transmitted audio quality.



