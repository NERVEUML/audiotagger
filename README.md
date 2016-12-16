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

Requirements
------------
We use [Direwolf](https://github.com/wb2osz/direwolf) for the TNC,
connected to a Signalink USB (though any form of radio interface would
work). On the decoding and sorting side, we use
[a fork](https://github.com/NERVEUML/multimon-ng) of
[multimon-ng](https://github.com/EliasOenal/multimon-ng), where our fork
outputs offsets into a file being decoded for APRS.

```
virtualenv -p python2 env
source env/bin/activate
pip install -r requirements.txt
```

Then there's a bunch of fragile, hacky code for decoding, organizing,
and cutting video files!

APRS
----
Since it's all APRS packets, there's suddenly a lot of capability for tagging videos
with location, weather, etc. And, since it's still ultimately an audio
track, you can always key up the correct channel with a walkie talkie
and save yourself some verbal notes or comments.
