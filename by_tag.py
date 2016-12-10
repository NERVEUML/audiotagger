#!/usr/bin/env python

#take in grep AFSK -b1 output, parse out the time, and spit out a time
#and duration based on tags for each filename, plus have a debug file
#that gives all tags in file in json.

import os
import re
import sys
import warnings
import fileinput
import datetime
from itertools import groupby

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

class Packet:
    def __init__(self, filename, threelines ):
        self.threelines = threelines
        self.filename = filename
        self.parsepacket()

    def parsepacket(self ):
        threelines = self.threelines
        #WARNING: depends on grep output to be stable, and must be updated with gentag.py, or will break!
        #Run tests when you install to be sure it works as expected.
        #depends on Time: lines always being printed before a packet is decoded (in practice this happens)
        #depends on multimon-ng output to be stable
        #print(threelines)
        s = None
        src = None
        dst = None
        pkt = None
        for line in threelines:
            m = re.match(fullmatch, line )
            if m == None:
                raise Exception("insufficient matches")
            bo = m.group("bo")
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
        #self.files = {p.filename for p in self.packets }
        self.calc()

    def calc(self):
        self.startoffset = self.packets[0].timeoffset
        self.endoffset = self.packets[-1].timeoffset
        self.fileduration = self.endoffset - self.startoffset

        self.start = self.packets[0].datetime
        self.end = self.packets[-1].datetime
        self.duration = (self.end - self.start).total_seconds()

    def __str__(self):
        return ("%s: \t+%d\t%6.2fs"%(
            runname(self.team, self.task, self.run),
            self.startoffset,
            self.duration
            ))
            
            
    
    
    
    
def parselines(filename, lines ):
    tlines = []
    packets = []
    ecount = 0
    for line in lines:
        #print(len(tlines), line)
        if line.strip() == "--":
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
        #5 is ballpark estimate of max number of three lines that shouldn't meet our expectations
        warnings.warn("The input file may not be matching our expectations, check input")
    packets.sort(key=lambda x: x.runname )
    return packets

def main( argv ):
    packets = parselines( 'stdin', fileinput.input() )
    runs = {}
    for k,v in groupby( packets, lambda x: x.runname ):
        plist = list(v)
        team = plist[0].team
        run = plist[0].run
        task = plist[0].task
        runs[k] = Run( team, task, run, plist )
        print( runs[k] )
    
        


def test():
    def split_iter(string):
        #https://stackoverflow.com/questions/3862010/is-there-a-generator-version-of-string-split-in-python
        return (x.group(0) for x in re.finditer(r"^.*$", string)) 

    ts="""
0:Enabled demodulators: AFSK1200
31-Time: 0.09,fbuf_cnt: 2048, acc=2048, secacc=0
--
3855-Time: 8.52,fbuf_cnt: 2066, acc=11444, secacc=8
3902:AFSK1200: fm WQYC60-9 to GPSLL-0 via WIDE1-1 UI  pid=F0
3958-{{T draper 4a 3.2 1479400526.886
--
11403-Time: 23.41,fbuf_cnt: 2066, acc=9098, secacc=23
11451:AFSK1200: fm WQYC60-9 to GPSLL-0 via WIDE1-1 UI  pid=F0
11507-{{T draper 4a 3.2 1479400541.902
--
148268-Time: 333.35,fbuf_cnt: 2066, acc=7780, secacc=333
148318:AFSK1200: fm WQYC60-9 to GPSLL-0 via WIDE1-1 UI  pid=F0
148374-{{S ssci 4a 3.1 1479400847.868 START
--
148513-Time: 333.82,fbuf_cnt: 4114, acc=18074, secacc=333
148564:AFSK1200: fm WQYC60-9 to GPSLL-0 via WIDE1-1 UI  pid=F0
148620-{{S ssci 4a 3.1 1479400847.868 START
--
"""
    parselines( 'test', ts.split("\n") )


if __name__ == "__main__":
    main( sys.argv )
    #test()