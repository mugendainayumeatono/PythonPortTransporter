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
    
    Objsock_service_linten = CTransport(10081,10082)
    #Objsock_service_linten.localSocket.pairing(Objsock_service_linten.remoteSocket)
    asyncore.loop(use_poll = True)
    
class clsbase:
    def donathing(self):
        pass
            
    
class clsa(clsbase):
    #def __init__(self):
        #self.m_objb=None
    def setobj(self,objb):
        self.m_objb = objb
    def showobjb(self):
        self.m_objb.showself()
        
class clsb(clsbase):
    def __init__(self):
        self.m_str = "hello"
    def showself(self):
        print(self.m_str)
class clsc:
    def __init__(self):
        self.obja = clsa()
        self.objb = clsb()
        self.obja.setobj(self.objb)
        self.obja.showobjb()
        self.obja.m_objb.value = 1

def testfun():
    objc = clsc()
    #objc.testfun()
    print(objc.obja.m_objb.value)
    print(objc.objb.value)

def main():
    nPotr = None
    nFlag = None
    testfun()
    if len(sys.argv) <= 1:
        usage()
    
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