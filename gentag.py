#!/usr/bin/env python

import os
import sys
import time
import aprs
import datetime
import logging

def packetize_me(me, you, path, name, task, run, data=None, now=None):
    if data == None:
        data = ""
    else:
        data = " " + str(data)
    frametypes={
            "tag":"T",
            "start":"S",
            }
    if not now:
        now=time.time()
        frametype="tag"
    else:
        frametype="start"
    frametxt = "{{%s %s %s %s %.03f%s"%(frametypes[frametype], name, task, run, now, data )
    framestr = "%s>%s,%s:%s"%( me, you, path, frametxt )
    frame = aprs.Frame( framestr )
    return frame

def send_event_start_frames(name, task, run, data=None, number_of_frames=5):
    print("Sending event start frames, count=%d"%( number_of_frames) )
    now=time.time()
    for i in range(number_of_frames):
        frame = packetize_me( me, you, path, name, task, run, data, now )
        import pdb; pdb.set_trace()
        k.write( frame )
        print(frame)

me = "WQYC60-9"
you = "GPSLL" #laptop
path = 'WIDE1-1'

if __name__ == "__main__":
    k = aprs.TCPKISS("localhost",8001)
    k._logger.setLevel(logging.DEBUG)
    k.start()

    delay = int( sys.argv[1] )
    name = sys.argv[2]
    task = sys.argv[3]
    run = sys.argv[4]


    send_event_start_frames( name, task, run, "START", 6)
    while 1:
        frame = packetize_me( me, you, path, name, task, run )
        print(frame)
        k.write( frame )
        print(frame)
        time.sleep( delay )

    
