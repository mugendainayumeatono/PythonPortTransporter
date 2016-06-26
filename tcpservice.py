import asyncore
import socket
import logging
# user module
from common import *
import protocol
#------------------------------------------------------------------------------
#
#调查为什么连接到remote的socket不会被关闭
#强化log
#
class CBase_socket(asyncore.dispatcher):
    #objLoger = None
    list_BlockAddr = []
    nRecvBuffSize = 1024
    #list_szSendBuff = []
    
    def __init__(self,sock=None,objParents=None,nSockID=None):
        asyncore.dispatcher.__init__(self,sock)
        if nSockID == None:
            self.objLoger = logging.getLogger('log.socket.listen')
        else:
            self.objLoger = logging.getLogger('log.socket.connect({})'.format(nSockID))
        if objParents!=None:
            self.objParents = objParents
        self.list_szSendBuff = []
        self.szBuff = []
        self.list_accepted_socket = {}
        self.nSocketID = 0
    
    def default_accept():
        pass
        
    def default_read(data):
        print (data)
    
    dict_Base_socket_MethodMatrix = {
        "accept":default_accept,
        "read":default_read
    }
    
    #overwrite this method in child class please
    def readMethod(self,data):
        self.dict_Base_socket_MethodMatrix["read"](data)
        
    def handle_accept(self):
        sock, addr = self.accept()
        if sock is not None:
            if addr in self.list_BlockAddr:
                self.objLoger.info ("blocked {}".format(addr))
                sock.close()
                return
            self.list_accepted_socket[self.nSocketID] = (self.__class__(sock,self,self.nSocketID))
            self.objLoger.debug ("construct socket ID:{}".format(self.nSocketID))
            self.nSocketID += 1
            self.dict_Base_socket_MethodMatrix["accept"]()
            self.objLoger.info ("connected from {}".format(addr))
        
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
            
            
class CClient_RemoteSocket(CBase_socket):
    
    def readadata(self,data):
        print("CClient_RemoteSocket")
        print(data)
        self.objRemoteSocket.sendData(data)
        
    def On_SetRemote(self,tuple_RemoteAddr):
        self.SetRemote(tuple_RemoteAddr)
        
    def On_FirstPacket(self,data):
        self.On_SetRemote(self.objParents.tuple_RemoteAddr)
        #check password
        self.objLoger.warning ("Error password")
        self.objRemoteSocket = CClient_RemoteSocket()
        self.objRemoteSocket.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.objRemoteSocket.connect(self.tuple_RemoteAddr)
        except(ConnectionError):
            self.handle_close()
        self.isFirstPacket = False
        self.sendData({"123":123})
        
    def On_LinkClose(self,data):
        self.objLoger.info ("disconnected {}".format(self.tuple_RemoteAddr))
        self.objRemoteSocket.close()
    
    dict_MethodMatrix = {
        "read":readadata,
        "firstpacket":On_FirstPacket,
        "linkclose":On_LinkClose,
        "setremote":On_SetRemote
    }
    
    def __init__(self,sock=None,objParents=None,nSocketID=None):
        CBase_socket.__init__(self,sock,objParents,nSocketID)
        self.UpdateMethodMatrix(self.dict_MethodMatrix)
        self.isFirstPacket = True
        
    def SetRemote(self,tuple_RemoteAddr):
        self.tuple_RemoteAddr = tuple_RemoteAddr
        self.objLoger.info ("set remote peer {}".format(self.tuple_RemoteAddr))
    
    def readMethod(self,data):
        if self.isFirstPacket:
            fun = self.GetMethod("firstpacket")
        elif(len(data) == 0):
            fun = self.GetMethod("linkclose")
        else:
            fun = self.GetMethod("read")
        fun(self,data)

class CClient_LocalSocket(CBase_socket):
    def __init__(self,sock=None):
        CBase_socket.__init__(self,sock)
        
    #def pairing(self,objSock):
    #    self.objLoger.info ("got remote socket {}")
    #    print(objSock.tmp)
    #    self.objPairSocket.append(objSock)
    
    def handle_read(self):
        #data = self.recv(self.nRecvBuffSize)
        #if(len(data) == 0):
        #     self.objLoger.info ("disconnected {}".format(self.addr))
        #     self.objPairSocket.close()
        #     return
        #self.objLoger.debug ("receive {} bit".format(len(data)))
        obj = self.objPairSocket.pop()
        print(obj.tmp)
        obj.list_szSendBuff.append(11)
        print(obj.list_szSendBuff.pop())
               
class CTransport():
    
    def method_echo(localSocket,data):
        localSocket.objLoger.debug ("echo {} bit data={}".format(len(dict_Data["data"]),dict_Data["data"]))
        localSocket.sendData(data)
        
    def localReadMethod(self,data):
        print("read")
        self.localSocket.objLoger.debug ("echo {} bit data={}".format(len(data),data))
        self.localSocket.sendData(data) 
    
    def method_accept(self):
        pass
    
    def method_read(self,data):
        self.objLoger.debug ("echo")
        return self.dict_MethodMatrix["echo"]

    dict_LocalMethodMatrix={
        "accept":method_accept,
        "read":method_read,
        "echo":localReadMethod
        #"pwd":method_checkPWD
    }
    
    dict_RemoteMethodMatrix={
        "echo":method_echo,
        #"pwd":method_checkPWD
    }

    def __init__(self, nLocalPort,nRemotePort):
        self.localSocket = CBase_socket()
        self.localSocket.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.localSocket.bind(("",nLocalPort))
        self.localSocket.listen(5)
        
        self.remoteSocket = CBase_socket()
        #self.remoteSocket.pairing(self.localSocket)
        #self.remoteSocket.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        #self.remoteSocket.bind(("",nRemotePort))
        #self.remoteSocket.listen(5)
        print("=======================")
        self.localSocket.pairing(self.remoteSocket)
        self.remoteSocket.pairing(self.localSocket)
        #self.remoteSocket.list_szSendBuff.append(10)
        #print(self.localSocket.objPairSocket.list_szSendBuff.pop())
        #self.localSocket.handle_read()
        print("=======================")