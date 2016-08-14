#!/usr/bin/env python

import os
import re
import sys
import time
import datetime
import string
import struct
import reedsolo

class NerveTRDescriptor:
    structformatstr = "!8sHHd"
    br = 120
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
        self.encoded =  b"\x7e"*int(self.br/4) + self.rs.encode( self.packed ) + b"\x7e"*int(self.br/8)
        #*2 the encoded portion maybe?  might try that with higher bitrates...
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
            f.write(n1.encoded)
        os.system("minimodem -t %d --stopbits 3.0 --startbits 3.0 < %s"%(n1.br,outfile))
        os.system("minimodem -t %d --stopbits 3.0 --startbits 3.0 < %s"%(n1.br*10,outfile))
        os.system("minimodem -t %d --stopbits 3.0 --startbits 3.0 < %s"%(n1.br*10,outfile))
        os.system("minimodem -t %d --stopbits 3.0 --startbits 3.0 < %s"%(n1.br*10,outfile))
    
