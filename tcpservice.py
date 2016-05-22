import asyncore
import socket
import logging
# user module
from common import *
import protocol
#------------------------------------------------------------------------------
#
#新想法，dict_RemoteMethodMatrix里面 填入全局函数或者类函数，两个socket 记录在类变量里面
#
# 值仅仅赋给了 linsten的那个socket，accept以后会产生新的socket 新socket没有被赋值！！！！！
# 由此引出的问题： 应该是先建立一个监听socket 每次accept成功产生新的socket，此时要再创建一个remote socket和accept的socket关联
#也就是 只能在on_accept函数里面创建remote socket
#
#
class CBase_socket(asyncore.dispatcher):
    #objTcpServiceLoger = None
    list_BlockAddr = []
    nRecvBuffSize = 1024
    list_szSendBuff = []
    
    def __init__(self,sock=None):
        asyncore.dispatcher.__init__(self,sock)
        self.objTcpServiceLoger = logging.getLogger('log.socket')
        self.list_szSendBuff = []
        self.szBuff = []
        self.list_accepted_socket = []
    
    def default_accept():
        pass
        
    def default_read(self,data):
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
        print("{}".format(self.list_BlockAddr))
        if sock is not None:
            if addr in self.list_BlockAddr:
                self.objTcpServiceLoger.info ("blocked {}".format(addr))
                sock.close()
                return
            self.list_accepted_socket.append(self.__class__(sock))
            self.dict_Base_socket_MethodMatrix["accept"]()
            self.objTcpServiceLoger.info ("connected {}".format(addr))
        
    def handle_read(self):
        data = self.recv(self.nRecvBuffSize)
        if(len(data) == 0):
             self.objTcpServiceLoger.info ("disconnected {}".format(self.addr))
             self.close()
             return
        self.objTcpServiceLoger.debug ("receive {} bit".format(len(data)))
        self.readMethod(data)


        
    def writable(self):
        if(len(self.szBuff)==0):
            try:
                self.szBuff = self.list_szSendBuff.pop()
            except IndexError:
                pass
    
        #self.objTcpServiceLoger.debug ("data={}({})".format(self.szBuff,len(self.szBuff)))
        return (len(self.szBuff) > 0)

    def handle_write(self):
        nLength = self.send(self.szBuff)
        #self.objTcpServiceLoger.debug ("send data {}({})".format(self.szBuff,len(self.szBuff)))
        self.objTcpServiceLoger.debug ("send {} bit".format(nLength))
        self.szBuff = self.szBuff[nLength:]
        #self.objTcpServiceLoger.debug ("has not send data {}({})".format(self.szSendBuff,len(self.szSendBuff)))
        
    def sendData(self,szData):
        self.list_szSendBuff.append(szData)
    
    @classmethod
    def AddToBlockAddr(cls,szIPaddr):
        cls.list_BlockAddr.append(szIPaddr)
        
    @classmethod
    def UpdateMethodMatrix(cls,dict_add):
        cls.dict_Base_socket_MethodMatrix.update(dict_add)
        
    @classmethod
    def GetMethod(cls,strMethod):
        return cls.dict_Base_socket_MethodMatrix[strMethod]
            
            
class CClient_RemoteSocket(CBase_socket):
    
    def readadata(self,data):
        print("CClient_RemoteSocket")
        print(data)
        self.sendData(data)
    
    dict_MethodMatrix = {
        "read":readadata
    }
    
    def __init__(self,sock=None):
        CBase_socket.__init__(self,sock)
        self.UpdateMethodMatrix(self.dict_MethodMatrix)
        self.isFirstPacket = True
    
    def readMethod(self,data):
        if self.isFirstPacket:
            #check password
            self.objTcpServiceLoger.warning ("Error password")
            self.objRemoteSocket = CClient_RemoteSocket()
            self.isFirstPacket = False
        else:
            fun = self.GetMethod("read")
            fun(self,data)

class CClient_LocalSocket(CBase_socket):
    def __init__(self,sock=None):
        CBase_socket.__init__(self,sock)
        
    #def pairing(self,objSock):
    #    self.objTcpServiceLoger.info ("got remote socket {}")
    #    print(objSock.tmp)
    #    self.objPairSocket.append(objSock)
    
    def handle_read(self):
        #data = self.recv(self.nRecvBuffSize)
        #if(len(data) == 0):
        #     self.objTcpServiceLoger.info ("disconnected {}".format(self.addr))
        #     self.objPairSocket.close()
        #     return
        #self.objTcpServiceLoger.debug ("receive {} bit".format(len(data)))
        obj = self.objPairSocket.pop()
        print(obj.tmp)
        obj.list_szSendBuff.append(11)
        print(obj.list_szSendBuff.pop())
               
class CTransport():
    
    def method_echo(localSocket,data):
        localSocket.objTcpServiceLoger.debug ("echo {} bit data={}".format(len(dict_Data["data"]),dict_Data["data"]))
        localSocket.sendData(data)
        
    def localReadMethod(self,data):
        print("read")
        self.localSocket.objTcpServiceLoger.debug ("echo {} bit data={}".format(len(data),data))
        self.localSocket.sendData(data) 
    
    def method_accept(self):
        pass
    
    def method_read(self,data):
        self.objTcpServiceLoger.debug ("echo")
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