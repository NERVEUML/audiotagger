#!/usr/bin/env python

import os
import sys
import time
import aprs
import signal
import socket
import datetime
import logging

try:
    from gps3.agps3threaded import AGPS3mechanism
    nogps = False
except:
    nogps = True
    pass

class nerveframetypes:
    tag = "T"
    start = "S"
    startreminder = "R"
    end = "E"

def packetize_me(me, you, path, frametype, name, task, run, data=None, now=None):
    if data == None:
        data = ""
    else:
        data = " " + str(data)
    if not now:
        now=time.time()

    frametxt = "{{%s %s %s %s %.2f%s"%( frametype, name, task, run, now, data )
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
    if len(sys.argv) < 5:
        print("""
        ./gentag.py delay_in_seconds team_name task_name run_id
        """)
        sys.exit(1)
    delay = float( sys.argv[1] )
    name = sys.argv[2]
    task = sys.argv[3]
    run = sys.argv[4]


    if not nogps:
        try:
            agps_thread = AGPS3mechanism()
            agps_thread.stream_data()
            agps_thread.run_thread()
        except socket.error as e:
            print("GPSD not running?")
            print(e)
            nogps = True


    k = aprs.TCPKISS("localhost",8001)

    #k._logger.setLevel(logging.WARNING)
    for key in logging.Logger.manager.loggerDict:
        logging.getLogger(key).setLevel(logging.WARNING)
        #print(key)

    while 1:
        try:
            #aprs tcpkiss, start connection
            k.start()
            break
        except socket.error as e:
            print(e)
            print("Retrying %s:%d"%(k.address))
        time.sleep(2)
    

    def signal_handler(signal, frame):
        print("Sending last frames....")
        now = time.time()
        endtime = send_many_frames(me, you, path, nerveframetypes.end, name, task, run, "END, duration %.2f"%(now - starttime), None,  5)
        time.sleep(1)
        print("Sent, exiting!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    starttime = send_many_frames( me, you, path, nerveframetypes.start, name, task, run, "START", None, 6)
    now = time.time()
    nexttag = now + delay
    nextstarttag = now + delay
    while 1:
        print(".")
        if not nogps:
            print('---------------------')
            print(                   agps_thread.data_stream.time)
            print('Lat:{}   '.format(agps_thread.data_stream.lat))
            print('Lon:{}   '.format(agps_thread.data_stream.lon))
            print('Speed:{} '.format(agps_thread.data_stream.speed))
            print('Course:{}'.format(agps_thread.data_stream.track))
            print('---------------------')
        now = time.time()
        if now >= nexttag:
            frame = packetize_me( me, you, path, nerveframetypes.tag, name, task, run, "running for %.2f"%( now - starttime ) )
            print(frame)
            k.write( frame )
            nexttag = now + delay
        if now >= nextstarttag:
            frame = packetize_me( me, you, path, nerveframetypes.startreminder, name, task, run, "startreminder", starttime )
            print(frame)
            k.write( frame )
            nextstarttag = now + delay*3
        time.sleep( delay/16 )

    
