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
import asyncore
import socket
import logging
import time
import queue
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, EINVAL, \
ENOTCONN, ESHUTDOWN, EISCONN, EBADF, ECONNABORTED, EPIPE, EAGAIN, \
errorcode
_DISCONNECTED = frozenset({ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE,EBADF})
# user module
from common import *
from encryption import *
#------------------------------------------------------------------------------
#
#
#readable() function to limit cache lenght
#
#
#
#doc
# on child class over write function readMethod() to define what will child class do
# readMethod() should call GetMethod() which get method form method martix table, to decide what will do
# use UpdateMethodMatrix() to update method martix table
# in CBase_socket there are two default method accept and read,you should overwrite those two method on child class
class CBase_socket(asyncore.dispatcher):
    #objLoger = None
    list_BlockAddr = []
    nRecvBuffSize = 4194304
    nQueueMaxLen = 5
    #nRecvBuffSize = 1024
    #list_szSendBuff = []
    
    def default_accept(self):
        pass

    def default_read(self,data):
        print (data)

    dict_CBase_socket_MethodMatrix = {
        "accept":default_accept,
        "read":default_read
    }

    def UpdateMethodMatrix(self,dict_add):
        self.dict_RunTime_MethodMatrix.update(dict_add)

    def __init__(self,sock=None,objParents=None,nSockID=None):
        asyncore.dispatcher.__init__(self,sock)
        if nSockID == None:
            self.objLoger = logging.getLogger('log.{}.listen'.format(self.__class__.__name__))
            self.nSocketID = None
            self.nIDCounter = 0
        else:
            self.objLoger = logging.getLogger('log.{}.connections({})'.format(self.__class__.__name__,nSockID))
            self.nSocketID = nSockID
        if objParents!=None:
            self.objParents = objParents
        self.list_szSendBuff = queue.Queue(self.nQueueMaxLen)
        self.szBuff = []
        self.list_accepted_socket = {}
        self.dict_RunTime_MethodMatrix ={}
        self.timeOut_flage = time.time()
        self.isWouldClose = False
        self.UpdateMethodMatrix(self.dict_CBase_socket_MethodMatrix)
    
    #overwrite this method in child class please
    def readMethod(self,data):
        self.dict_RunTime_MethodMatrix["read"](self,data)
        
    def create_socket(self, family=socket.AF_INET, type=socket.SOCK_STREAM,protocal=0):
        self.family_and_type = family, type
        sock = socket.socket(family, type,protocal)
        sock.setblocking(0)
        self.set_socket(sock)
        
    def handle_accept(self):
        sock, addr = self.accept()
        self.objLoger.info ("accept peer {}".format(self.addr))
        if sock is not None:
            if self.addr in self.list_BlockAddr:
                self.objLoger.warning ("blocked {}".format(self.addr))
                sock.close()
                return
            self.objLoger.debug ("constructed transport socket ID:{}".format(self.nIDCounter))
            self.list_accepted_socket[self.nIDCounter] = (self.__class__(sock,self,self.nIDCounter))
            #set peer name
            self.list_accepted_socket[self.nIDCounter].peerAddr = addr
            if self.nIDCounter == 65535:
                self.nIDCounter =0
            else:
                self.nIDCounter += 1
            self.dict_RunTime_MethodMatrix["accept"](self)
        
    def handle_read(self):
        data = self.recv(self.nRecvBuffSize)
        #
        self.timeOut_flage = time.time()
        self.objLoger.debug ("timestamp={}".format(self.timeOut_flage))
        # if len(data)==0 then link was alredy closed
        self.objLoger.debug ("receive {} bit".format(len(data)))
        #self.objLoger.debug ("read {}({})".format(data,len(data)))
        self.readMethod(data)
        
    def checkSendCache(self):
        if(len(self.szBuff)==0):
            try:
                self.szBuff = self.list_szSendBuff.get_nowait()
            except queue.Empty:
                pass
    
        #self.objLoger.debug ("check send cache {}".format(len(self.szBuff) > 0))
        return (len(self.szBuff) > 0)
    
    def writable(self):
        if self.checkSendCache():
            return True
        else:
            if self.isWouldClose:
                # socket would like close,and try to send cache data out, now cache was enpty so we can turely close socket
                self.objLoger.debug ("cache data was cleaned try to truely close socket")
                self.handle_close()
            else:
                return False

    #if timeout close connection
    def readable(self):
        if (self.nSocketID == None):
            # listen socket will not timeout
            return True
            
        self.objLoger.debug ("timeout check(time={}s)".format(time.time()-self.timeOut_flage))
        if(time.time()-self.timeOut_flage>TIMEOUTTIME):
            self.objLoger.warning ("long time not receive data auto close connection(time={}s)".format(time.time()-self.timeOut_flage))
            self.handle_close()
            return False
        else:
            return True

    def handle_write(self):
        self.objLoger.debug ("will send {} bit".format(len(self.szBuff)))
        nLength = self.send(self.szBuff)
        #self.objLoger.debug ("send data {}({})".format(self.szBuff,len(self.szBuff)))
        self.szBuff = self.szBuff[nLength:]
        self.objLoger.debug ("has not send data {} bit".format(len(self.szBuff)))
        
    def handle_close(self, isGentle=True):
        if hasattr(self,"peerAddr"):
            peerAddr = self.peerAddr
        else:
            try:
                peerAddr = self.socket.getpeername()
            except Exception:
                peerAddr = "unknow"
        
        if self.connected == False:
            self.objLoger.debug ("already disconnected {}".format(peerAddr))
        else:
            if isGentle == True:
                if self.isWouldClose ==False:
                    self.isWouldClose =True
                    self.objLoger.info ("socket {} would close".format(self.nSocketID))
                    self.handle_shutDownRead()
                    return
                else:
                    # if isWouldClose is True means we second times call handle_close
                    # May be the cache was empty  and we can tryely close socket,or when clean cahce there were something wrong like socket has already closed
                    if self.checkSendCache():
                        self.objLoger.warning ("there were something wrong occurred,we do not gentle disconnect cache date was got lost")
            else:
                self.objLoger.debug ("skip gentle disconnect")
        self.close()
        self.objLoger.info ("disconnected {}".format(peerAddr))
        if (self.nSocketID == None):
            # current socket is listen socket
            self.objLoger.debug ("listen socket closed")
        else:
            if hasattr(self,"objParents"):
               self.objParents.list_accepted_socket[self.nSocketID] = None
            self.objLoger.debug ("destruct transport socket ID:{}".format(self.nSocketID))
            
    def handle_connect(self):
        self.peerAddr = self.socket.getpeername()
        self.objLoger.debug ("connected to {}".format(self.peerAddr))
        
    def handle_error(self):
        traceback_error(self.objLoger,self)
        self.handle_close(False)
 
    # bFlage == True shutdown read,bFlage == False shutdown write
    def handle_shutDownRead(self):
        self.objLoger.debug ("shutdown read {}".format(self.addr))
        self.socket.shutdown(socket.SHUT_RD)
       
    def sendData(self,szData):
        try:
            self.list_szSendBuff.put_nowait(szData)
        except queue.Full:
            self.objLoger.error ("put data to buffer fail, data get lost, send buffer was full!")
    
    @classmethod
    def AddToBlockAddr(cls,szIPaddr):
        cls.list_BlockAddr.append(szIPaddr)
        
    #overwrite this method in child class please
    #@classmethod
    #def GetMethod(cls,strMethod):
    #    return cls.dict_RunTime_MethodMatrix[strMethod]
        
    def GetMethod(self,strMethod):
        return self.dict_RunTime_MethodMatrix[strMethod]   


class CMiddleSocketLayer(CBase_socket):
    
    def __init__(self,sock=None,objParents=None,nSocketID=None):
        CBase_socket.__init__(self,sock,objParents,nSocketID)
        
    def readMethod(self,data):
        if len(data)==0:
            fun = self.GetMethod("linkclose")
        else:
            fun = self.GetMethod("read")
        fun(self,data)

    #
    #nConnectionMode 0: do NoT Encrypt
    #nConnectionMode 1: Encrypt data as server peer
    #nConnectionMode 2: Encrypt data as client peer
    #otherwise do NoT Encrypt
    #
    def selfConfigure(self,tuple_RemoteAddr,nConnectionMode,szPassWord = None):
        self.nConnectionMode = nConnectionMode
        self.tuple_RemoteAddr = tuple_RemoteAddr
        self.szPassWord = szPassWord
        self.objLoger.info ("transport target {}".format(self.tuple_RemoteAddr))
            
        if self.nConnectionMode == SERVER_MODE:
            self.objLoger.info ("Server Encryption Mode!")
            self.UpdateMethodMatrix(self.dict_ServerMethodMatrix)
        elif self.nConnectionMode == CLIENT_MODE:
            self.objLoger.info ("Client Encryption Mode!")
            self.UpdateMethodMatrix(self.dict_ClientMethodMatrix)	
        #self.nConnectionMode ==0
        else:
            self.objLoger.info ("Normal Mode!")
            self.UpdateMethodMatrix(self.dict_MethodMatrix)
            
        if self.nConnectionMode == SERVER_MODE or self.nConnectionMode == CLIENT_MODE:
            if szPassWord == None:
                raise ValueErroe("Encryption must specify a password")
            else:
                self.encryptor,self.decryptor = creatTwoEncryptor(szPassWord)


class CLocalSocket(CMiddleSocketLayer):
    
    def __init__(self,sock=None,objParents=None,nSocketID=None):
        CMiddleSocketLayer.__init__(self,sock,objParents,nSocketID)
        self.objLoger.debug ("Socket ID:{}".format(nSocketID))
        
        if objParents != None:
            self.selfConfigure(objParents.tuple_RemoteAddr,self.objParents.nConnectionMode,self.objParents.szPassWord)
            
    def readable(self):
        def checkBufferOfRemoteSocket(self):
            if (self.nSocketID != None):
            
                if not hasattr(self,"objRemoteSocket"):
                    self.objLoger.debug ("donot has objRemoteSocket")
                    self.GetMethod("creatremote")(self)
                if self.objRemoteSocket.list_szSendBuff.qsize() >= self.nQueueMaxLen-2:
                    self.objLoger.info ("sent buffer full")
                    return False
                else:
                    return True
            else:
                #listen socket donot need check buffer
                return True
        bRet_timeOutCheck=CMiddleSocketLayer.readable(self)
        bRet_bufferCheck=checkBufferOfRemoteSocket(self)
        return bRet_timeOutCheck&bRet_bufferCheck
        
    def On_Receivedata(self,data):
        if hasattr(self,"objRemoteSocket") == False:
            self.GetMethod("creatremote")(self)
        self.objLoger.debug ("transport:{} bit".format(len(data)))
        self.objRemoteSocket.sendData(data)
        
    def On_Receivedata_Encrypt(self,data):
        self.objLoger.debug ("encrypt")
        self.On_Receivedata(self.encryptor.encrypt(data))

    def On_Receivedata_Decrypt(self,data):
        self.objLoger.debug ("decrypt")
        self.On_Receivedata(self.decryptor.decrypt(data))
        
    def On_LinkClose(self,data):
        self.objLoger.debug ("close remote{}".format(self.objParents.tuple_RemoteAddr))
        if hasattr(self,"objRemoteSocket") == True:
            self.objRemoteSocket.handle_close()

    #
    #nEnableEncryption 0: do NoT Encrypt
    #nEnableEncryption 1: Encrypt data as server peer
    #nEnableEncryption 2: Encrypt data as client peer
    #otherwise do NoT Encrypt
    #
    def On_ConnecToRemote(self):
        self.objLoger.debug ("connect to {}".format(self.objParents.tuple_RemoteAddr))
        self.objRemoteSocket.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.objRemoteSocket.connect(self.objParents.tuple_RemoteAddr)
        except(ConnectionError):
            self.objLoger.error ("connect to {} fail".format(self.objParents.tuple_RemoteAddr))
            self.handle_close(False)

    def On_CreatRemote_Normal(self):
        self.objLoger.debug ("normal creat remote socket")
        self.objRemoteSocket = CRemoteSocket(None,self,self.nSocketID)
        self.On_ConnecToRemote()

    def On_CreatRemote_Server(self):
        self.objLoger.debug ("server peer creat remote socket")
        self.objRemoteSocket = CRemoteSocket(None,self,self.nSocketID)
        self.On_ConnecToRemote()

    def On_CreatRemote_Client(self):
        self.objLoger.debug ("client peer creat remote socket")
        self.objRemoteSocket = CRemoteSocket(None,self,self.nSocketID)
        self.On_ConnecToRemote()

    dict_MethodMatrix = {
        #"accept":On_Accept,
        "creatremote":On_CreatRemote_Normal,
        "read":On_Receivedata,
        "linkclose":On_LinkClose,
    }

    dict_ClientMethodMatrix = {
        #"accept":On_Accept,
        "creatremote":On_CreatRemote_Client,
        "read":On_Receivedata_Encrypt,
        "linkclose":On_LinkClose,
    }


    dict_ServerMethodMatrix = {
        #"accept":On_Accept,
        "creatremote":On_CreatRemote_Server,
        "read":On_Receivedata_Decrypt,
        "linkclose":On_LinkClose,
    }

class CRemoteSocket(CMiddleSocketLayer):
    def readable(self):
        def checkBufferOfRemoteSocket(self):
            if self.objLocalSocket.list_szSendBuff.qsize() >= self.nQueueMaxLen-2:
                self.objLoger.info ("sent buffer full")
                return False
            else:
                return True
                
        bRet_timeOutCheck=CMiddleSocketLayer.readable(self)
        bRet_bufferCheck=checkBufferOfRemoteSocket(self)
        return bRet_timeOutCheck&bRet_bufferCheck

    
    def On_Receivedata(self,data):
        self.objLoger.debug ("transport:{} bit".format(len(data)))
        self.objLocalSocket.sendData(data)

    def On_Receivedata_Encryption(self,data):
        self.objLoger.debug ("encrypt")
        self.On_Receivedata(self.encryptor.encrypt(data))

    def On_Receivedata_Decryption(self,data):
        self.objLoger.debug ("decrypt")
        self.On_Receivedata(self.decryptor.decrypt(data))

    def On_LinkClose(self,data):
        self.objLoger.debug ("remote closed {}".format(self.objLocalSocket.tuple_RemoteAddr))
        self.objLocalSocket.handle_close()

    dict_MethodMatrix = {
        "read":On_Receivedata,
        "linkclose":On_LinkClose
    }

    dict_ServerMethodMatrix = {
        "read":On_Receivedata_Encryption,
        "linkclose":On_LinkClose
    }

    dict_ClientMethodMatrix = {
        "read":On_Receivedata_Decryption,
        "linkclose":On_LinkClose
    }

    def __init__(self,sock=None,objLocalSocket=None,nSockID=None):
        CMiddleSocketLayer.__init__(self,None,None,objLocalSocket.nSocketID)
        self.objLoger.debug ("socket ID:{}".format(objLocalSocket.nSocketID) + ",init " + self.__class__.__name__)
        self.UpdateMethodMatrix(self.dict_MethodMatrix)
        if objLocalSocket != None:
            self.objLocalSocket = objLocalSocket
            self.selfConfigure(objLocalSocket.tuple_RemoteAddr,objLocalSocket.nConnectionMode,objLocalSocket.szPassWord)
        else:
            raise AssertionError("must input parameter objLocalSocket,CRemoteSocket must initialize by CLocalSocket")
    
if __name__ == '__main__' :
    tuple_RemoteAddr = ("127.0.0.1",22)
    tuple_LocalAddr = ("127.0.0.1",10087)
    tuple_LocalAddrForEncryption = ("127.0.0.1",10080)
    szPassWord = "12345678"
    index = 1
    globefunStartLog("debug",True)
    objLoger = logging.getLogger('log.main')

    def normal():
        objListen = CLocalSocket()
        objListen.selfConfigure(tuple_RemoteAddr,NORMAL_MODE)
        objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        objListen.bind(tuple_LocalAddr)
        objListen.listen(5)
        
        objSent = CBase_socket()
        objSent.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        objSent.connect(tuple_LocalAddr)
        print("connect complete")
        objSent.sendData(b"test data")
        asyncore.loop(use_poll = True)

    def encryption():
        objListen = CLocalSocket()
        objListen.selfConfigure(tuple_LocalAddrForEncryption,CLIENT_MODE,szPassWord)
        objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        objListen.bind(tuple_LocalAddr)
        objListen.listen(5)
        objLoger.info ("listen {}".format(tuple_LocalAddr))
        objLoger.info ("Client Ready")

        objListen2 = CLocalSocket()
        objListen2.selfConfigure(tuple_RemoteAddr,SERVER_MODE,szPassWord)
        objListen2.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        objListen2.bind(tuple_LocalAddrForEncryption)
        objListen2.listen(5)
        objLoger.info ("listen {}".format(tuple_LocalAddrForEncryption))
        objLoger.info ("Server Ready")

        objSent = CBase_socket()
        objSent.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        objSent.connect(tuple_LocalAddr)
        objLoger.info ("Sent test data")
        objSent.sendData(b"test data")
        asyncore.loop(use_poll = True)

    table = [normal,encryption]

    table[index]()
