#!/usr/bin/env python

#take in grep AFSK -b1 output, parse out the time, and spit out a time
#and duration based on tags for each filename, plus have a debug file
#that gives all tags in file in json.

import os
import re
import sys
import json
import warnings
import fileinput
import datetime
import hashlib
from itertools import groupby



#if a class has a tojson method, use that for encoding it.
from json import JSONEncoder
def _default(self, obj):
    return getattr(obj.__class__, "tojson", _default.default)(obj)
_default.default = JSONEncoder().default
JSONEncoder.default = _default

packets = r"{{" + \
            "(?P<type>\w)" +"\s+"+ \
            "(?P<team>\S+)" +"\s+"+ \
            "(?P<task>\S+)" +"\s+"+ \
            "(?P<run>\S+)" +"\s+"+ \
            "(?P<epoch>\S+)" +\
            "(?P<comment>.*)"

byteoffset = r"(?P<bo>\d+)"
matchorcontext = r"(?P<mn>[:-])"

timematch = r"(?P<time>Time: (?P<seconds>\d+.\d+))"
headermatch = r"(?P<header>AFSK\w+: \w+ (?P<src>\S+) to (?P<dst>\S+))"
packetmatch = r"(?P<packet>{{.*\n?)"

linematch = r"(?P<l>%(timematch)s|%(headermatch)s|%(packetmatch)s)" % locals()

fullmatch = r"%(byteoffset)s%(matchorcontext)s%(linematch)s" % locals()

#(\d+)([:-])((Time: (\d+.\d+))|(AFSK\w+: \w+ (\S+) to (\S+))|({{.*\n))

def runname( team, task, run ):
    return "%s_%s_%s"%( team, task, run )

def get_orig_fn_from_aprs_file( aprsdatafilename ):
    aprsdataending = ".orig.aprs"
    oldnameending = ".oldname"
    assert aprsdatafilename.endswith( aprsdataending )
    oldnamefile = aprsdatafilename[: - len(aprsdataending)] + oldnameending
    with open(oldnamefile,"r") as f:
        original_name = f.read().strip()
        real_name = os.path.realpath( original_name )
        assert os.path.samefile( real_name, original_name )
        return real_name
    


class Packet:
    def __init__(self, filename, threelines ):
        self.threelines = threelines
        self.filename = filename
        self.parsepacket()

    def parsepacket(self ):
        threelines = self.threelines
        #WARNING: depends on grep output to be stable, and must be updated with gentag.py, or will break!
        #Run tests when you install to be sure it works as expected.
        #depends on Time: lines always being printed before a packet is decoded
        #depends on multimon-ng output to be stable
        #depends on grep output to be stable
        #if the output of any of these changes, this is what to fix, plus all the regexes that are defined globally in this by_tag.py file.
        #print(threelines)
        s = None
        src = None
        dst = None
        pkt = None
        for line in threelines:
            m = re.match(fullmatch, line )
            if m == None:
                raise Exception("insufficient matches")
            bo = m.group("bo") #byte offset (grep output)
            mn = True if m.group("mn") == ":" else False
            if m.group("time"):
                s = m.group("seconds")
            if m.group("header"):
                src = m.group("src")
                dst = m.group("dst")
            if m.group("packet"):
                pkt = m.group("packet")
        self.timeoffsetstr = s
        self.timeoffset = float(s)
        self.src = src
        self.dst = dst
        self.pkt = pkt
        
        parsed_pkt = re.match( packets, pkt )
        self.type = parsed_pkt.group("type")
        self.team = parsed_pkt.group("team")
        self.task = parsed_pkt.group("task")
        self.run = parsed_pkt.group("run")
        self.epochstr = parsed_pkt.group("epoch")
        self.comment = parsed_pkt.group("comment")
        self.epoch = float( self.epochstr )
        self.datetime = datetime.datetime.fromtimestamp( self.epoch )
        self.runname = runname( self.team, self.task, self.run )

    def __str__(self):
        return("%s +% 9.2f  @%.2f \t%s %s %s # %s"%(
            os.path.basename(self.filename),
            self.timeoffset,
            self.epoch,
            self.team,
            self.task,
            self.run,
            self.comment
        ))


class Run:
    def __init__(self, team, task, run, packets):
        self.team = team
        self.task = task
        self.run = run
        self.packets = sorted( packets, key=lambda x: x.epoch )
        self.runname = runname(self.team, self.task, self.run)
        self.files = {p.filename for p in self.packets }
        #originally written for multiple files

        #BUT used for only one at a time now
        assert len(self.files) == 1
        self.file = [p for p in self.files][0]

        self.videofile = [get_orig_fn_from_aprs_file(p) for p in self.files ][0]
        self.calc()

    def calc(self):
        """
        Figure start and end offsets into file, and real times, based on first and last packets that were decoded.
        Also figure duration.
        """
        self.startoffset = self.packets[0].timeoffset
        self.endoffset = self.packets[-1].timeoffset
        self.fileduration = self.endoffset - self.startoffset

        self.start = self.packets[0].datetime
        self.end = self.packets[-1].datetime
        self.duration = (self.end - self.start).total_seconds()
    
    def tojson(self):
        """Used by json encoder to serialize this object"""
        me = {
            "runname": self.runname,
            "team":self.team,
            "task":self.task,
            "run":self.run,
            "start":self.start.isoformat(),
            "startoffset":self.startoffset,
            "duration":self.duration,
            "file": self.file,
            "videofile": self.videofile
            }
        return me

    def __str__(self):
        return ("%s %d %6.2f"%(
            self.runname,
            self.startoffset,
            self.duration
            ))
    def ffmpegme(self):
        """Generate ffmpeg lines for cutting the file"""
        out = "_".join([ 
                    self.runname, 
                    hashlib.md5(self.videofile.encode("utf-8")).hexdigest()[:10]
                    ]) + self.videofile[-4:] 
        startoffset = self.startoffset - 30 #offset to allow context
        duration = self.duration + 60 #offset for context, and some more because not all packets decoded properly on all videos
        videofile = self.videofile
        #-ss is start time
        #-t is duration
        #-to is end time
        #also see this:
        #https://blog.yimingliu.com/2008/10/07/ffmpeg-encoding-gotchas/
        return "ffmpeg -ss %(startoffset)d -t %(duration)d -i %(videofile)s -c copy %(out)s"% locals()

    
def parselines(filename, lines ):
    """
    Given APRS lines (from filename, which is just to tell each
    Packet where it is from), parse them into packets and return
    the packet objects.  This expects multimon-ng output from the
    NERVEUML/multimon-ng fork, which includes decoded packet offset data
    before the decoded packet is printed.
    """
    tlines = []  #temporary set of lines, to be passed to Packet
    packets = [] #successfully decoded packets that will be returned
    ecount = 0 #count of number of times tlines wasn't able to be decoded
    for line in lines: #build up lines until we have enough to be a packet, then try and decode and add to packets array
        #print(len(tlines), line)
        if line.strip() == "--": #a line matching '^--$' separates decoded packets, because of how we use grep.
            try:
                p = Packet( filename, tlines )
                packets.append(p)
            except Exception as e:
                #print(e)
                ecount+=1
            tlines=[]
        else:
            tlines.append(line)
    if ecount >= 5:
        #5 is ballpark estimate of max number of groups of three lines that shouldn't meet our expectations
        warnings.warn("The input file may not be matching our expectations, check input")

    packets.sort(key=lambda x: x.runname )
    return packets #return packets sorted by runname

def main( argv ):
    """
    by_tag.py   <a filename>
    A filename is the name of the video file being decoded.
    optional arguments ending in .json and .ffmpeg will be filled with the decoded packets in json format, 
        and ffmpeg command lines to automatically cut the file.
    you can have zero, either, or both of these, and order does not matter.

    stdout will get a sorted summary list of runs printed to screen
    """
    #TODO real argument handling
    jsonfile = None
    ffmpegfile = None
    if len(argv) < 2:
        print("provide a filename")
        sys.exit(1)
    filename = argv[1]
    if len(argv) > 2:
        for x in argv[2:]:
            if x.endswith(".json"):
                jsonfile = x
            if x.endswith(".ffmpeg"):
                ffmpegfile = x
    #packets = parselines( 'stdin', fileinput.input() ) #will read lines from stdin or from filenames as arguments
    packets = parselines( filename, sys.stdin.readlines() ) #just reads lines from stdin

    # dump summary to screen
    runs = {}
    for k,v in groupby( packets, lambda x: x.runname ):
        plist = list(v)
        team = plist[0].team
        run = plist[0].run
        task = plist[0].task
        runs[k] = Run( team, task, run, plist )
        print(runs[k])

    if jsonfile: #dump packets to the json file
        with open(jsonfile,"w") as f:
            f.write( json.dumps( runs ))

    if ffmpegfile: #dump ffmpeg command lines to the ffmpeg file (you can cut files automatically with these command lines)
        with open(ffmpegfile,"w") as f:
            for runname,run in runs.items():
                f.write("%s\n"%(run.ffmpegme()))



def test():
    def split_iter(string):
        #https://stackoverflow.com/questions/3862010/is-there-a-generator-version-of-string-split-in-python
        return (x.group(0) for x in re.finditer(r"^.*$", string)) 

    ts="""
0:Enabled demodulators: AFSK1200
31-Time: 0.09,fbuf_cnt: 2048, acc=2048, secacc=0
--
3855-Time: 8.52,fbuf_cnt: 2066, acc=11444, secacc=8
3902:AFSK1200: fm callsign-9 to GPSLL-0 via WIDE1-1 UI  pid=F0
3958-{{T team2 4a 3.2 1479400526.886
--
11403-Time: 23.41,fbuf_cnt: 2066, acc=9098, secacc=23
11451:AFSK1200: fm callsign-9 to GPSLL-0 via WIDE1-1 UI  pid=F0
11507-{{T team2 4a 3.2 1479400541.902
--
148268-Time: 333.35,fbuf_cnt: 2066, acc=7780, secacc=333
148318:AFSK1200: fm callsign-9 to GPSLL-0 via WIDE1-1 UI  pid=F0
148374-{{S team1 4a 3.1 1479400847.868 START
--
148513-Time: 333.82,fbuf_cnt: 4114, acc=18074, secacc=333
148564:AFSK1200: fm callsign-9 to GPSLL-0 via WIDE1-1 UI  pid=F0
148620-{{S team1 4a 3.1 1479400847.868 START
--
"""
    parselines( 'test', ts.split("\n") )


if __name__ == "__main__":
    main( sys.argv )
    #test()
