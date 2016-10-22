#
#    PythonPotrTransporter
#    Copyright (C) 2016 by mickeyyf
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import logging
import getopt
import sys
import time
# user module
from common import *
from service import *

def usage():
    print("-n        normal proxy,local will connect to remote")
    print("-c        start as client peer connection will encrypt")
    print("-s        start as server peer connection will encrypt")
    print("-C        upper case -C,Contrary proxy,remote will connect to local, this is ues for cross local NAT")
    print("-d        debug")
    print("--key     encryption keyword,lenght must 16 byte")
    print("--ip      set remote ip adderss")
    print("--lport   set local port")
    print("--rport   set remote port")
    
def startService(nLocalPort,szRemoteIP,nRemotePort):
    
    tuple_RemoteAddr = (szRemoteIP,nRemotePort)
    tuple_LocalAddr = ("",nLocalPort)
    
    objListen = CLocalSocket()
    objListen.selfConfigure(tuple_RemoteAddr,NORMAL_MODE)
    objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objListen.bind(tuple_LocalAddr)
    objListen.listen(5)
    asyncore.loop(use_poll = True)

def startEncryptionService_AsClient(nLocalPort,szRemoteIP,nRemotePort,szKey):
    tuple_RemoteAddr = (szRemoteIP,nRemotePort)
    tuple_LocalAddr = ("",nLocalPort)

    objListen = CLocalSocket()
    objListen.selfConfigure(tuple_RemoteAddr,CLIENT_MODE,szKey)
    objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objListen.bind(tuple_LocalAddr)
    objListen.listen(5)
    asyncore.loop(use_poll = True)

def startEncryptionService_AsServer(nLocalPort,szRemoteIP,nRemotePort,szKey):
    tuple_RemoteAddr = (szRemoteIP,nRemotePort)
    tuple_LocalAddr = ("",nLocalPort)

    objListen2 = CLocalSocket()
    objListen2.selfConfigure(tuple_RemoteAddr,SERVER_MODE,szKey)
    objListen2.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objListen2.bind(tuple_LocalAddr)
    objListen2.listen(5)
    asyncore.loop(use_poll = True)


def main():
    szloglevel = "info"
    nFlag = 0
    if len(sys.argv) <= 1:
        usage()
        sys.exit(2)
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ncsChd",["ip=","lport=","rport=","key="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for eachOpt, eachArg in opts:
        if eachOpt == "--ip":
            try:
                szRemoteIP = str(eachArg)
            except ValueError:
                print("ip must be a string")
                sys.exit(2)
        elif eachOpt == "--lport":
            try:
                nLocalPort = int(eachArg)
            except ValueError:
                print("potr must be a number")
                sys.exit(2)
        elif eachOpt == "--rport":
            try:
                nRemotePort = int(eachArg)
            except ValueError:
                print("potr must be a number")
                sys.exit(2)
        elif eachOpt == "--key":
            if len(eachArg) != 16:
                print("lenght of key must 16 byte")
                sys.exit(2)
            else:
                szKey = eachArg
        elif eachOpt == "-n":
            nFlag = nFlag | NORMAL_PROXY
        elif eachOpt == "-c":
            nFlag = nFlag | ENCRYPT_CLIENT
        elif eachOpt == "-s":
            nFlag = nFlag | ENCRYPT_SERVER
        elif eachOpt == "-C":
            nFlag = nFlag | CONTRARY_PROXY
        elif eachOpt == "-d":
            szloglevel = "debug"
        elif eachOpt == "-h":
            usage()
            sys.exit()
        else:
            print("unknow option {}".format(eachOpt))
            usage()
            sys.exit(2)
           

    objMainLoger = logging.getLogger('log.main')
    globefunStartLog(szloglevel,False)
    
    #check param
    if not "nLocalPort" in locals():
        print("must specify local port")
        sys.exit(2)
    if not "szRemoteIP" in locals():
        print("must specify remote ip")
        sys.exit(2)
    if not "nRemotePort" in locals():
        print("must specify remote port")
        sys.exit(2)
    if (nFlag & ENCRYPTION) != 0:
        if not "szKey" in locals():
            print("must specify a key")
            sys.exit(2)

    objMainLoger.info("start at {}".format(time.asctime()))
    if nFlag == NORMAL_PROXY:
        startService(nLocalPort,szRemoteIP,nRemotePort)
    elif nFlag == ENCRYPT_CLIENT:
        startEncryptionService_AsClient(nLocalPort,szRemoteIP,nRemotePort,szKey)
    elif nFlag == ENCRYPT_SERVER:
        startEncryptionService_AsServer(nLocalPort,szRemoteIP,nRemotePort,szKey)
    else:
        print("-n -s or -c must chose only one")
        sys.exit(2)
        
    
    
if __name__ == '__main__' :
    main()
