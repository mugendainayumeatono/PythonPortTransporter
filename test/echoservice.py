import os,sys
import logging
import getopt
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
from tcpservice import *

class CEcho_socket(CBase_socket):
    def __init__(self,sock=None,objParents=None,nSocketID=None):
        CBase_socket.__init__(self,sock,objParents,nSocketID)
    		
    def readMethod(self,data):
        self.sendData(data)

def main():
    def usage():
        print("parameter will look like '-p port'")
    
    nPotr = None
    if len(sys.argv) <= 1:
        usage()
        sys.exit(2)
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:")
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for eachOpt, eachArg in opts:
        if eachOpt == "-p":
            try:
                nPotr = int(eachArg)
            except ValueError:
                print("potr must be a number")
                sys.exit(2)
        else:
            print("unknow option {}".format(eachOpt))
            usage()
            sys.exit(2)

    globefunStartLog("debug",True)
    objListen = CEcho_socket()
    objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objListen.bind(("",nPotr))
    objListen.listen(5)
    objListen.objLoger.info ("Start echo serviec")
    asyncore.loop(use_poll = True)


if __name__ == '__main__' :
    main()