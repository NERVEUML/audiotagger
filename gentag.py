#!/usr/bin/env python

import os
import sys
import time
import string
import struct
import reedsolo

class NerveTRDescriptor:
    structformatstr = "!xx8sxHxHxdxx"
    def __init__(self, *args,**kwargs):
        self.rs=reedsolo.RSCodec(150)
        if( len(args) == 1 ):
            self.encoded = args[0]
            self.decode()
            print( self.sane() )
            return
            if not self.decode() or not self.sane():
                print(self.__str__(), "not sane, trying next down")
                if len( self.encoded ) >=  struct.calcsize( self.structformatstr ):
                    try:
                        self.__init__( self.encoded[1:] )
                    except Exception as e:
                        pass
                else:
                    raise Exception("insane!")
            else:
                # pass
                print("sane!")
                print(self.__str__())
                # print("next...")
                # size = struct.calcsize( self.structformatstr )
                # self.__init__( self.encoded[size:] )
        else:
            self.group = args[0]
            self.task = args[1]
            self.run = args[2]
            self.timestamp = args[3]
            self.encode()

    def encode(self):
        # self.packed = struct.pack(self.structformatstr, bytes(self.group,'ascii') , self.task, self.run, self.timestamp)
        #self.encoded = b"^"*10 + self.rs.encode( self.packed ) + b"."*10
        # self.encoded = b" "*5 + self.rs.encode( self.packed ) + b" "*5
        self.encoded =  self.rs.encode( self.__str__() ) 
        return self

    
    def decode(self):
        # self.strippedencoded = self.encoded.lstrip(b"^")
        # self.strippedencoded = self.strippedencoded.rstrip(b".")
        # self.packed = self.rs.decode( self.strippedencoded )
        try:
            self.unpacked = self.rs.decode( self.encoded)
            # self.packed = self.rs.decode( self.encoded)
            # self.unpacked = struct.unpack_from( self.structformatstr, self.packed)
            # self.group, self.task, self.run, self.timestamp = self.unpacked
            self.group, self.task, self.run, self.timestamp = self.unpacked
            self.group = self.group.decode('ascii')
            self.task = int(self.task)
            self.run = int(self.run)
        except Exception as e:
            # print(e)
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
            print(self.task, self.run)
            return False

    def sanets(self):
        try:
            # time.time( self.timestamp )
            return self.timestamp > 1467837142 #right now as I code it!
        except Exception as e:
            # print(e)
            # print("not sane ts")
            return False
        return True

    def sane(self):
        print("Group sane: ",self.sanegroup()) 
        print("TaskRuns sane: ",self.sanetr())
        print("TimeStamp sane: ",self.sanets())
        return self.sanegroup() and self.sanetr() and self.sanets()

    def showme(self):
        print(self.__str__() )

    def __str__(self):
        return "%s: %d.%d %f"%(self.group, self.task, self.run, self.timestamp)

if __name__ == "__main__":
    if sys.argv[1] == "in":
        with open( sys.argv[2], "rb") as f:
            data=f.read()
        n2 = NerveTRDescriptor(data)
        n2.showme()
    elif sys.argv[1] == "out":
        outfile = "nerveafsk.out"
        n1 = NerveTRDescriptor(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]), time.time() )
        with open( outfile ,"wb") as f:
            f.write(n1.encoded)
        os.system("minimodem -t 300 --stopbits 3.0 --startbits 3.0 < " + outfile)
    
