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

class NERVETRError( Exception ):
    pass

class FrameFlagInPacket( NERVETRError):
    """Frame Flag detected in packet data
    """
    pass




class NerveTRDescriptor:
    structformatstr = "!8sHHd"
    br = 1200
    frameflag = b'\x7e'
    def __init__(self, *args,**kwargs):
        self.rs=reedsolo.RSCodec(10)
        if "br" in kwargs:
            self.br = kwargs["br"]
        if( len(args) == 1 ):
            self.encoded = args[0]
            self.decodeall()
        else:
            self.group = args[0]
            self.task = args[1]
            self.run = args[2]
            self.timestamp = args[3]
            self.encode()

    def encode(self):
        self.packed = struct.pack( self.structformatstr, bytes(self.group,'ascii'), self.task, self.run, self.timestamp )
        self.encoded =   self.rs.encode( self.packed ) 
        if self.frameflag in self.encoded:
            print( str(self.encoded ))
            print( self.encoded )
            print( binascii.hexlify(self.encoded ))
            raise FrameFlagInPacket("FrameFlag %s detected in packet!"%(self.frameflag));
        # try /4 and /8 later
        pre = 20
        post = 40
        sendme = self.frameflag*int(self.br/pre) + self.encoded + self.frameflag*int(self.br/post)
        self.encoded = sendme
        
        return self

    def decodeall(self):
        self.packets = re.split( b'\x7e+', self.encoded)
        for pkt in self.packets:
            self.decode(pkt)

    def decode(self, pkt):
        if len(pkt) < struct.calcsize( self.structformatstr ):
            return False
        # print(pkt)
        try:
            self.packed = self.rs.decode( pkt )
            self.unpacked = struct.unpack_from(self.structformatstr, self.packed)
            self.group, self.task, self.run, self.timestamp = self.unpacked
            self.group = self.group.decode('ascii')
            self.showme()
        except Exception as e:
            return False
        return True

    def sanegroup(self):
        return True
        return all(c in string.printable for c in self.group)

    def sanetr(self):
        if self.task > 0 and self.run > 0 :
            print("tr sane")
            return True
        else:
            # print(self.task, self.run)
            return False

    def sanets(self):
        try:
            return self.timestamp > 1467837142 #right now as I code it!
        except Exception as e:
            print(e)
            # print("not sane ts")
            return False
        return True

    def sane(self):
        print("Group sane: ",self.sanegroup()) 
        print("TaskRuns sane: ",self.sanetr())
        print("TimeStamp sane: ",self.sanets())
        return self.sanegroup() and self.sanetr() and self.sanets()

    def showme(self):
        print(self.__str__(), "\t", datetime.datetime.fromtimestamp( self.timestamp).strftime('%Y-%m-%d %H:%M:%S') )

    def __str__(self):
        try:
            return "%s:  \t%d.%02d  \t%f"%(self.group, self.task, self.run, self.timestamp)
        except:
            return "Invalid"

if __name__ == "__main__":
    if sys.argv[1] == "in":
        filename_endings=re.compile('_\d+.txt')
        for fn in sys.argv[2:]:
            video_filename = filename_endings.sub("",fn)
            print(video_filename)
            with open( fn, "rb") as f:
                data=f.read()
            n2 = NerveTRDescriptor(data)
            print()
    elif sys.argv[1] == "out":
        outfile = "nerveafsk.out"
        n1 = NerveTRDescriptor(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]), time.time() )
        with open( outfile ,"wb") as f:
            # f.write( b"~"*1000)
            f.write(n1.encoded)
        # os.system("minimodem -t %d < %s"%(300,outfile))
        os.system("minimodem -t %d < %s"%(n1.br,outfile))
    elif sys.argv[1] == 'direwolf':
        k = aprs.APRSKISS(host="localhost",tcp_port=8001)
        k._logger.setLevel(logging.DEBUG)
        k.start()


        me = "WQYC60-9"
        you = "GPSLL" #laptop
        path = 'WIDE1-1'
        name = sys.argv[3]
        task = sys.argv[4]
        run = sys.argv[5]
        delay = int( sys.argv[2] )
        try:
            sys.argv[6]
            quiet = True
        except:
            quiet = False

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

        if not quiet:
            send_event_start_frames( name, task, run, "START", 6)
        while 1:
            frame = packetize_me( me, you, path, name, task, run )
            k.write( frame )
            print(frame)
            time.sleep( delay )

    elif sys.argv[1] == "kissout":
        k = kiss.KISS(sys.argv[2],speed=9600)
        k._logger.setLevel(logging.DEBUG)
        k.start()
        # k.start(**kiss.constants.DEFAULT_KISS_CONFIG_VALUES)
        while 1:
            try:
                # n1 = NerveTRDescriptor(sys.argv[3],int(sys.argv[4]),int(sys.argv[5]), time.time() )
                # k.write( n1.encoded )
                k.write(b'.'*10)
            except FrameFlagInPacket as e:
                
                print("Accidentally tried to break the rules and put a frameflag in the middle of the packet")
                print("this is not a problem is sending by modem, except then we can't yet decode it!")
                print(" ")
                
            time.sleep(4)
        # k.read(callback=print)
    else:
        usage(sys.argv)
    
