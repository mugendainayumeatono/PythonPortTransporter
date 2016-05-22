import logging
import getopt
import sys
# user module
from common import *
from tcpservice import *

def usage():
    print("-s start as service")
    
def startService(port):
    print(port)
    #addr = "192.168.1.2"
    addr = ""
    #port = 10080
    
    objMainLoger = logging.getLogger('log.main')
    globefunStartLog("debug",True)
    objMainLoger.debug("helloword")
    
    Objsock_service_linten = CClient_RemoteSocket()
    Objsock_service_linten.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    Objsock_service_linten.bind(("",10081))
    Objsock_service_linten.listen(5)
    #Objsock_service_linten.localSocket.pairing(Objsock_service_linten.remoteSocket)
    asyncore.loop(use_poll = True)

def main():
    nPotr = None
    nFlag = None
    if len(sys.argv) <= 1:
        usage()
        sys.exit(2)
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "scp:h")
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
        elif eachOpt == "-h":
            usage()
            sys.exit()
        elif eachOpt == "-s":
            nFlag = 0
        else:
            print("unknow option {}".format(eachOpt))
            usage()
            sys.exit(2)
            
    if nFlag == 0:
        startService(nPotr)
    elif nFlag == 1:
        pass
    else:
        print("error arguments")
        usage()
        sys.exit(2)
        
    
    
if __name__ == '__main__' :
    main()