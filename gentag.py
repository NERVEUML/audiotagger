#!/usr/bin/env python

import os
import sys
import time
import aprs
import signal
import datetime
import logging

class nerveframetypes:
    tag = "T"
    start = "S"
    end = "E"

def packetize_me(me, you, path, frametype, name, task, run, data=None, now=None):
    if data == None:
        data = ""
    else:
        data = " " + str(data)
    if not now:
        now=time.time()

    frametxt = "{{%s %s %s %s %.03f%s"%( frametype, name, task, run, now, data )
    framestr = "%s>%s,%s:%s"%( me, you, path, frametxt )
    frame = aprs.Frame( framestr )
    return frame

def send_many_frames( me, you, path, frametype, name, task, run, data=None, now=None, number_of_frames=5):
    if not now:
        now=time.time()
    for i in range(number_of_frames):
        frame = packetize_me( me, you, path, frametype, name, task, run, data, now )
        k.write( frame )
        print(frame)
    return now

me = "WQYC60-9"
you = "GPSLL" #laptop
path = 'WIDE1-1'
starttime = None

if __name__ == "__main__":
    k = aprs.TCPKISS("localhost",8001)
    k._logger.setLevel(logging.DEBUG)
    k.start()

    delay = int( sys.argv[1] )
    name = sys.argv[2]
    task = sys.argv[3]
    run = sys.argv[4]

    def signal_handler(signal, frame):
        print("Sending last frames....")
        endtime = send_many_frames(me, you, path, nerveframetypes.end, name, task, run, "END", None,  2)
        f = packetize_me( me, you, path, nerveframetypes.start, name, task, run, "START", starttime )
        k.write( f )
        send_many_frames(me, you, path, nerveframetypes.end, name, task, run, "END", endtime,  3)
        time.sleep(1)
        print("Sent, exiting!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    starttime = send_many_frames( me, you, path, nerveframetypes.start, name, task, run, "START", None, 6)
    now = time.time()
    nexttag = now + delay
    nextstarttag = now + delay
    while 1:
        now = time.time()
        if now >= nexttag:
            frame = packetize_me( me, you, path, nerveframetypes.tag, name, task, run )
            print(frame)
            k.write( frame )
            nexttag = now + delay
        if now >= nextstarttag:
            frame = packetize_me( me, you, path, nerveframetypes.start, name, task, run, "START", starttime )
            print(frame)
            k.write( frame )
            nextstarttag = now + delay*7
        time.sleep( delay/8 )

    
