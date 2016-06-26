import asyncore
import socket
import logging
import time
# user module
from common import *
import protocol
#------------------------------------------------------------------------------
# 矩阵表 类似有化
#
#doc
# on child class over write function readMethod() to define what will child class do
# readMethod() should call GetMethod() which get method form method martix table, to decide what will do
# use UpdateMethodMatrix() to update method martix table
# in CBase_socket there aer two default method accept and read,you should overwrite those two method on child class
class CBase_socket(asyncore.dispatcher):
    #objLoger = None
    list_BlockAddr = []
    nRecvBuffSize = 1024
    #list_szSendBuff = []
    
    def __init__(self,sock=None,objParents=None,nSockID=None):
        asyncore.dispatcher.__init__(self,sock)
        if nSockID == None:
            self.objLoger = logging.getLogger('log.{}.listen'.format(self.__class__.__name__))
            self.nSocketID = 0
        else:
            self.objLoger = logging.getLogger('log.{}.connect({})'.format(self.__class__.__name__,nSockID))
            self.nSocketID = nSockID
        if objParents!=None:
            self.objParents = objParents
        self.list_szSendBuff = []
        self.szBuff = []
        self.list_accepted_socket = {}
    
    def default_accept(self):
        pass
        
    def default_read(self,data):
        print (data)
    
    dict_Base_socket_MethodMatrix = {
        "accept":default_accept,
        "read":default_read
    }
    
    #overwrite this method in child class please
    def readMethod(self,data):
        self.dict_Base_socket_MethodMatrix["read"](self,data)
        
    def create_socket(self, family=socket.AF_INET, type=socket.SOCK_STREAM,protocal=0):
        self.family_and_type = family, type
        sock = socket.socket(family, type,protocal)
        sock.setblocking(0)
        self.set_socket(sock)
        
    def handle_accept(self):
        sock, addr = self.accept()
        self.objLoger.info ("connected from {}".format(addr))
        if sock is not None:
            if addr in self.list_BlockAddr:
                self.objLoger.info ("blocked {}".format(addr))
                sock.close()
                return
            self.list_accepted_socket[self.nSocketID] = (self.__class__(sock,self,self.nSocketID))
            self.objLoger.debug ("constructed socket ID:{}".format(self.nSocketID))
            self.nSocketID += 1
            self.dict_Base_socket_MethodMatrix["accept"](self)
        
    def handle_read(self):
        data = self.recv(self.nRecvBuffSize)
        self.objLoger.debug ("receive {} bit".format(len(data)))
        self.readMethod(data)
        
    def writable(self):
        if(len(self.szBuff)==0):
            try:
                self.szBuff = self.list_szSendBuff.pop()
            except IndexError:
                pass
    
        #self.objLoger.debug ("data={}({})".format(self.szBuff,len(self.szBuff)))
        return (len(self.szBuff) > 0)

    def handle_write(self):
        nLength = self.send(self.szBuff)
        #self.objLoger.debug ("send data {}({})".format(self.szBuff,len(self.szBuff)))
        self.objLoger.debug ("send {} bit".format(nLength))
        self.szBuff = self.szBuff[nLength:]
        #self.objLoger.debug ("has not send data {}({})".format(self.szSendBuff,len(self.szSendBuff)))
        
    def handle_close(self):
        self.objLoger.info ("disconnected {}".format(self.addr))
        self.close()
        try:
            objParents = getattr(self, 'objParents')
        except AttributeError:
            self.objLoger.debug ("destruct socket ID:{}".format(self.nSocketID))
        else:
            self.objLoger.debug ("destruct socket ID:{}".format(self.nSocketID))
            self.objParents.list_accepted_socket[self.nSocketID] = None
            
    def handle_connect(self):
        self.objLoger.info ("connected to {}".format(self.addr))
        
    def sendData(self,szData):
        self.list_szSendBuff.append(szData)
    
    @classmethod
    def AddToBlockAddr(cls,szIPaddr):
        cls.list_BlockAddr.append(szIPaddr)
        
    @classmethod
    def UpdateMethodMatrix(cls,dict_add):
        cls.dict_Base_socket_MethodMatrix.update(dict_add)
    
    #overwrite this method in child class please
    @classmethod
    def GetMethod(cls,strMethod):
        return cls.dict_Base_socket_MethodMatrix[strMethod]     
            
            
class CClient_LocalSocket(CBase_socket):
    def SetRemote(self,tuple_RemoteAddr):
        self.tuple_RemoteAddr = tuple_RemoteAddr
        self.objLoger.info ("set remote peer {}".format(self.tuple_RemoteAddr))
    
    def On_Receivedata(self,data):
        self.objLoger.debug ("transport:{} bit".format(len(data))
        self.objRemoteSocket.sendData(data)
        
    def On_SetRemote(self,tuple_RemoteAddr):
        self.SetRemote(tuple_RemoteAddr)
        
    def On_RequestPWD(self,data):
        #check password
        self.objLoger.warning ("Error password")
        
    def On_LinkClose(self,data):
        self.objLoger.info ("remote disconnected {}".format(self.tuple_RemoteAddr))
        self.objRemoteSocket.close()
        
    def On_CreatRemote(self):
        self.objLoger.info ("creat remote socket and connect")
        self.objRemoteSocket = CClient_RemoteSocket(self)
        self.objRemoteSocket.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.objRemoteSocket.connect(self.objParents.tuple_RemoteAddr)
        except(ConnectionError):
            self.handle_close()
    
    dict_MethodMatrix = {
        #"accept":On_Accept,
        "read":On_Receivedata,
        "linkclose":On_LinkClose,
        "setremote":On_SetRemote
    }
    
    def __init__(self,sock=None,objParents=None,nSocketID=None):
        CBase_socket.__init__(self,sock,objParents,nSocketID)
        self.objLoger.debug ("init " + self.__class__.__name__)
        self.UpdateMethodMatrix(self.dict_MethodMatrix)
        if sock != None:
            self.On_CreatRemote()
    
    def readMethod(self,data):

        if(len(data) == 0):
            fun = self.GetMethod("linkclose")
        else:
            fun = self.GetMethod("read")
            fun(self,data)

class CClient_RemoteSocket(CBase_socket):
    def __init__(self,objLocalSocket):
        CBase_socket.__init__(self,None)
        self.objLoger.info ("socket ID:{}".format(objLocalSocket.nSocketID) + ",init " + self.__class__.__name__)
        self.objLocalSocket = objLocalSocket
        
    def readMethod(self,data):

        if(len(data) == 0):
        		self.objLoger.info ("server disconnected {}".format(self.tuple_RemoteAddr))
        		self.objLocalSocket.close()
        else:
            self.objLocalSocket.sendData(data)
        
if __name__ == '__main__' :
    tuple_RemoteAddr = ("127.0.0.1",10085)
    tuple_LocalAddr = ("127.0.0.1",10084)
    globefunStartLog("debug",True)
    
    objListen = CClient_LocalSocket()
    objListen.SetRemote(tuple_RemoteAddr)
    objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objListen.bind(tuple_LocalAddr)
    objListen.listen(5)

    time.sleep(1)
        
    objSent = CBase_socket()
    objSent.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objSent.connect(tuple_LocalAddr)
    print("connect complete")
    objSent.sendData(b"test data")
    #objListen.close()
    asyncore.loop(use_poll = True)
