import logging
import getopt
import sys
# user module
from common import *
from tcpservice import *

def usage():
    print("-n        normal start,local connect to remote")
    print("-c        contrary connect,remote connect to local, this is ues for cross local NAT")
    print("--ip      set remote ip adderss")
    print("--lport   set local port")
    print("--rport   set remote port")
    
def startService(nLocalPort,szRemoteIP,nRemotePort):
    
    tuple_RemoteAddr = (szRemoteIP,nRemotePort)
    tuple_LocalAddr = ("",nLocalPort)
    
    objListen = CLocalSocket()
    objListen.SetRemote(tuple_RemoteAddr)
    objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objListen.bind(tuple_LocalAddr)
    objListen.listen(5)
    asyncore.loop(use_poll = True)

def main():
    objMainLoger = logging.getLogger('log.main')
    globefunStartLog("debug",True)
    
    nFlag = 0
    if len(sys.argv) <= 1:
        usage()
        sys.exit(2)
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "nch",["ip=","lport=","rport="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for eachOpt, eachArg in opts:
        if eachOpt == "--ip":
            try:
                #print(eachArg)
                szRemoteIP = str(eachArg)
            except ValueError:
                print("ip must be a string")
                sys.exit(2)
        elif eachOpt == "--lport":
            try:
                #print(eachArg)
                nLocalPort = int(eachArg)
            except ValueError:
                print("potr must be a number")
                sys.exit(2)
        elif eachOpt == "--rport":
            try:
                #print(eachArg)
                nRemotePort = int(eachArg)
            except ValueError:
                print("potr must be a number")
                sys.exit(2)
        elif eachOpt == "-n":
            nFlag = nFlag | 1 #nFlag | 00000001b
        elif eachOpt == "-c":
            nFlag = nFlag | 2 #nFlag | 00000010b
        elif eachOpt == "-h":
            usage()
            sys.exit()
        else:
            print("unknow option {}".format(eachOpt))
            usage()
            sys.exit(2)
            
    #first bit enable
    if nFlag == 1:
        startService(nLocalPort,szRemoteIP,nRemotePort)
    #second bit enable
    elif nFlag == 2:
        pass
    #if first and second bit all enable nFlag will equal 3
    else:
        print("-c or -n must chose only one")
        usage()
        sys.exit(2)
        
    
    
if __name__ == '__main__' :
    main()