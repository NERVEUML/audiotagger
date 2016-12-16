#!/usr/bin/env python

import os
import re
import sys
import time
import kiss
import aprs
import datetime
import binascii
import string
import struct
import reedsolo
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
    frame = {
            'source':me,
            'destination':you,
            'path':path,
            'text':"{{%s %s %s %s %.03f%s"%(frametypes[frametype], name, task, run, now, data )
            }
    return frame

def send_event_start_frames(name, task, run, data=None, number_of_frames=5):
    print("Sending event start frames, count=%d"%( number_of_frames) )
    now=time.time()
    for i in range(number_of_frames):
        frame = packetize_me( me, you, path, name, task, run, data, now )
        k.write( frame )
        print(frame)

me = "WQYC60-9"
you = "GPSLL" #laptop
path = 'WIDE1-1'

if __name__ == "__main__":
    if sys.argv[1] == 'direwolf':
        k = aprs.APRSKISS(host="localhost",tcp_port=8001)
        k._logger.setLevel(logging.DEBUG)
        k.start()


        name = sys.argv[3]
        task = sys.argv[4]
        run = sys.argv[5]
        delay = int( sys.argv[2] )
        try:
            sys.argv[6]
            quiet = True
        except:
            quiet = False


        if not quiet:
            send_event_start_frames( name, task, run, "START", 6)
        while 1:
            frame = packetize_me( me, you, path, name, task, run )
            k.write( frame )
            print(frame)
            time.sleep( delay )

    else:
        usage(sys.argv)
    
