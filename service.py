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
    #nRecvBuffSize = 4194304
    nRecvBuffSize = 1024
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
        self.list_szSendBuff = queue.Queue()
        self.szBuff = []
        self.list_accepted_socket = {}
        self.dict_RunTime_MethodMatrix ={}
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
        self.objLoger.info ("connected from {}".format(addr))
        if sock is not None:
            if addr in self.list_BlockAddr:
                self.objLoger.info ("blocked {}".format(addr))
                sock.close()
                return
            self.objLoger.debug ("constructed transport socket ID:{}".format(self.nIDCounter))
            self.list_accepted_socket[self.nIDCounter] = (self.__class__(sock,self,self.nIDCounter))
            if self.nIDCounter == 65535:
                self.nIDCounter =0
            else:
                self.nIDCounter += 1
            self.dict_RunTime_MethodMatrix["accept"](self)
        
    def handle_read(self):
        data = self.recv(self.nRecvBuffSize)
        # if len(data)==0 then link was alredy closed
        self.objLoger.debug ("receive {} bit".format(len(data)))
        #self.objLoger.debug ("data {}({})".format(self.szBuff,len(self.szBuff)))
        self.readMethod(data)
        
    def writable(self):
        if(len(self.szBuff)==0):
            try:
                self.szBuff = self.list_szSendBuff.get_nowait()
            except queue.Empty:
                pass
    
        #self.objLoger.debug ("data={}({})".format(self.szBuff,len(self.szBuff)))
        return (len(self.szBuff) > 0)

    def handle_write(self):
        self.objLoger.debug ("will send {} bit".format(len(self.szBuff)))
        nLength = self.send(self.szBuff)
        #self.objLoger.debug ("send data {}({})".format(self.szBuff,len(self.szBuff)))
        self.szBuff = self.szBuff[nLength:]
        self.objLoger.debug ("has not send data {} bit".format(len(self.szBuff)))
        
    def handle_close(self, isGentle=True):
        self.objLoger.info ("do gentle disconnected {}".format(self.addr))
        if self.connected == False:
            self.objLoger.info("NO connect")
        else:
            if isGentle == True:
                # try to sent out cache data
                while self.writable():
                    try:
                        self.objLoger.debug ("will send {} bit".format(len(self.szBuff)))
                        nLength = self.socket.send(self.szBuff)
                        self.szBuff = self.szBuff[nLength:]
                    except OSError as why:
                        if why.args[0] in _DISCONNECTED:
                           self.objLoger.error ("gentle disconnect fail,cache data was got lost!!!")
                           break
            else:
                self.objLoger.info ("skip gentle")
        self.objLoger.info ("disconnected {}".format(self.addr))
        self.close()
        if hasattr(self, 'objParents') == False:
            # current socket is listen socket
            self.objLoger.debug ("destruct socket ID:{}".format(self.nSocketID))
        else:
            self.objParents.list_accepted_socket[self.nSocketID] = None
            self.objLoger.debug ("destruct transport socket ID:{}".format(self.nSocketID))
            
    def handle_connect(self):
        self.objLoger.info ("connected to {}".format(self.addr))
 
    # bFlage == True shutdown read,bFlage == False shutdown write
    def handle_shutdown(self,bFlage):
        if bFlage == True:
            self.objLoger.info ("shutdown read {}".format(self.addr))
            self.socket.shutdown(socket.SHUT_RD)
        else:
            #clean writ cache
            while self.writable():
                try:
                    nLength = self.socket.send(self.szBuff)
                    self.szBuff = self.szBuff[nLength:]
                except OSError as why:
                    if why.args[0] in _DISCONNECTED:
                        self.objLoger.error ("NO gentle disconnect,cache data was got lost!!!")
                        break

            self.objLoger.info ("shutdown write {}".format(self.addr))
            self.socket.shutdown(socket.SHUT_WR)  
       
    def sendData(self,szData):
        try:
            self.list_szSendBuff.put_nowait(szData)
        except queue.Full:
            self.objLoger.error ("send buffer was full!".format(self.nSocketID))
    
    @classmethod
    def AddToBlockAddr(cls,szIPaddr):
        cls.list_BlockAddr.append(szIPaddr)
        
    #overwrite this method in child class please
    #@classmethod
    #def GetMethod(cls,strMethod):
    #    return cls.dict_RunTime_MethodMatrix[strMethod]
        
    def GetMethod(self,strMethod):
        return self.dict_RunTime_MethodMatrix[strMethod]   


class CLocalSocket(CBase_socket):

    def SetRemote(self,tuple_RemoteAddr):
        self.tuple_RemoteAddr = tuple_RemoteAddr
        self.objLoger.info ("set transport target {}".format(self.tuple_RemoteAddr))
    
    def On_Receivedata(self,data):
        if hasattr(self,"objRemoteSocket") == False:
            self.GetMethod("creatremote")(self)
        self.objLoger.debug ("transport:{} bit".format(len(data)))
        self.objRemoteSocket.sendData(data)

    def On_Receivedata_Client(self,data):
        self.objLoger.debug ("encrypt")
        self.On_Receivedata(encrypt(data))

    def On_Receivedata_Server(self,data):
        if hasattr(self,"byteReceiveBuffer"):
            self.byteReceiveBuffer = self.byteReceiveBuffer.join(data)
        else:
            self.byteReceiveBuffer = data
        if len(self.byteReceiveBuffer)%16 != 0:
            self.objLoger.debug ("len of ReceiveBuffer {}".format(len(self.byteReceiveBuffer)))
            return
        else:
            self.objLoger.debug ("decrypt")
            self.On_Receivedata(decrypt(self.byteReceiveBuffer))
            self.byteReceiveBuffer = None

    def On_SetRemote(self,tuple_RemoteAddr):
        self.SetRemote(tuple_RemoteAddr)
        
    def On_RequestPWD(self,data):
        #check password
        self.objLoger.warning ("Error password")
        
    def On_LinkClose(self,data):
        self.objLoger.info ("disconnect remote {}".format(self.objParents.tuple_RemoteAddr))
        self.objRemoteSocket.handle_close()
    #
    #nEnableEncryption 0: do NoT Encrypt
    #nEnableEncryption 1: Encrypt data as server peer
    #nEnableEncryption 2: Encrypt data as client peer
    #otherwise do NoT Encrypt
    #
    def On_ConnecToRemote(self):
        self.objLoger.info ("creat remote socket and connect to {}".format(self.objParents.tuple_RemoteAddr))

        self.objRemoteSocket.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.objRemoteSocket.connect(self.objParents.tuple_RemoteAddr)
        except(ConnectionError):
            self.objLoger.warning ("connect to {} fail".format(self.objParents.tuple_RemoteAddr))
            self.handle_close(False)

    def On_CreatRemote_Normal(self):
       self.objRemoteSocket = CRemoteSocket(None,self,self.nSocketID)
       self.On_ConnecToRemote()

    def On_CreatRemote_Server(self):
        self.objRemoteSocket = CRemoteSocket(None,self,self.nSocketID)
        #self.objRemoteSocket.enableEncryption(True)
        self.objRemoteSocket.setSocketClass(SERVER_MODE)
        self.On_ConnecToRemote()

    def On_CreatRemote_Client(self):
        self.objRemoteSocket = CRemoteSocket(None,self,self.nSocketID)
        #self.objRemoteSocket.enableEncryption(False)
        self.objRemoteSocket.setSocketClass(CLIENT_MODE)
        self.On_ConnecToRemote()
    
    dict_MethodMatrix = {
        #"accept":On_Accept,
        "creatremote":On_CreatRemote_Normal,
        "read":On_Receivedata,
        "linkclose":On_LinkClose,
        "setremote":On_SetRemote
    }

    dict_ClientMethodMatrix = {
        #"accept":On_Accept,
        "creatremote":On_CreatRemote_Client,
        "read":On_Receivedata_Client,
        "linkclose":On_LinkClose,
        "setremote":On_SetRemote
    }


    dict_ServerMethodMatrix = {
        #"accept":On_Accept,
        "creatremote":On_CreatRemote_Server,
        "read":On_Receivedata_Server,
        "linkclose":On_LinkClose,
        "setremote":On_SetRemote
    }
    
    def __init__(self,sock=None,objParents=None,nSocketID=None):
        CBase_socket.__init__(self,sock,objParents,nSocketID)
        self.objLoger.debug ("Socket ID:{}".format(nSocketID) + "init " + self.__class__.__name__)
        
        if objParents != None:
            self.SetRemote(self.objParents.tuple_RemoteAddr)
            self.setSocketClass(self.objParents.nConnectionMode)
            
    def readMethod(self,data):
        if len(data)==0:
            fun = self.GetMethod("linkclose")
        else:
            fun = self.GetMethod("read")
        fun(self,data)
        

    def enableEncryption(self,szEncrypticKey,bIsServer):
        self.szEncrypticKey = szEncrypticKey
        self.bIsServer = bIsServer
        setAESEncryptionKey(szEncrypticKey)
        if bIsServer == True:
            self.UpdateMethodMatrix(self.dict_ServerMethodMatrix)
            self.objLoger.info ("Encryption Server Mode!")
        else:
            self.UpdateMethodMatrix(self.dict_ClientMethodMatrix)
            self.objLoger.info ("Encryption Client Mode!")
        self.UpdateMethodMatrix(self.dict_MethodMatrix)


    #
    #nConnectionMode 0: do NoT Encrypt
    #nConnectionMode 1: Encrypt data as server peer
    #nConnectionMode 2: Encrypt data as client peer
    #otherwise do NoT Encrypt
    #
    def setSocketClass(self,nConnectionMode):
        self.nConnectionMode = nConnectionMode
            
        if self.nConnectionMode == SERVER_MODE:
            self.objLoger.info ("Encryption Server Mode!")
            self.UpdateMethodMatrix(self.dict_ServerMethodMatrix)
        elif self.nConnectionMode == CLIENT_MODE:
            self.objLoger.info ("Encryption Client Mode!")
            self.UpdateMethodMatrix(self.dict_ClientMethodMatrix)	
        # elif  self.nConnectionMode ==0
        else:
            self.objLoger.info ("Normal Mode!")
            self.UpdateMethodMatrix(self.dict_MethodMatrix)


class CRemoteSocket(CBase_socket):
    def On_Receivedata(self,data):
        self.objLoger.debug ("transport:{} bit".format(len(data)))
        self.objLocalSocket.sendData(data)

    def On_Receivedata_Encryption(self,data):
        self.objLoger.debug ("encrypt")
        self.On_Receivedata(encrypt(data))

    def On_Receivedata_Decryption(self,data):
        if hasattr(self,"byteReceiveBuffer"):
            self.byteReceiveBuffer = self.byteReceiveBuffer.join(data)
        else:
            self.byteReceiveBuffer = data
        if len(self.byteReceiveBuffer)%16 != 0:
            self.objLoger.debug ("len of ReceiveBuffer {}".format(len(self.byteReceiveBuffer)))
            return
        else:
            self.objLoger.debug ("decrypt")
            self.On_Receivedata(decrypt(self.byteReceiveBuffer))
            self.byteReceiveBuffer = None



    def On_LinkClose(self,data):
        self.objLoger.info ("server disconnected {}".format(self.objLocalSocket.tuple_RemoteAddr))
        self.objLocalSocket.handle_close()

    dict_MethodMatrix = {
        "read":On_Receivedata,
        "linkclose":On_LinkClose
    }

    dict_MethodMatrix_Encryption = {
        "read":On_Receivedata_Encryption,
        "linkclose":On_LinkClose
    }

    dict_MethodMatrix_Decryption = {
        "read":On_Receivedata_Decryption,
        "linkclose":On_LinkClose
    }

    def __init__(self,sock=None,objParents=None,nSockID=None):
        CBase_socket.__init__(self,None,None,objParents.nSocketID)
        self.objLoger.info ("socket ID:{}".format(objParents.nSocketID) + ",init " + self.__class__.__name__)
        self.objLocalSocket = objParents
        self.UpdateMethodMatrix(self.dict_MethodMatrix)
        
    def readMethod(self,data):
        if len(data)==0:
            fun = self.GetMethod("linkclose")
        else:
            fun = self.GetMethod("read")
        fun(self,data)


    def enableEncryption(self,bIsServer):
        #setAESencryptKey(szEncrypticKey)
        if bIsServer == True:
            self.UpdateMethodMatrix(self.dict_MethodMatrix_Decryption)
            self.objLoger.info ("Encryption Server Mode!")
        else:
            self.UpdateMethodMatrix(self.dict_MethodMatrix_Encryption)
            self.objLoger.info ("Encryption Client Mode!")
            
    def setSocketClass(self,nConnectionMode):
        self.nConnectionMode = nConnectionMode
            
        if self.nConnectionMode == SERVER_MODE:
            self.objLoger.info ("Encryption Server Mode!")
            self.UpdateMethodMatrix(self.dict_MethodMatrix_Encryption)
        elif self.nConnectionMode == CLIENT_MODE:
            self.objLoger.info ("Encryption Client Mode!")
            self.UpdateMethodMatrix(self.dict_MethodMatrix_Decryption)	
        # elif  self.nConnectionMode ==0
        else:
            self.objLoger.info ("Normal Mode!")
            self.UpdateMethodMatrix(self.dict_MethodMatrix)
    
if __name__ == '__main__' :
    tuple_RemoteAddr = ("127.0.0.1",22)
    tuple_LocalAddr = ("127.0.0.1",10087)
    tuple_LocalAddrForEncryption = ("127.0.0.1",10080)
    index = 1
    globefunStartLog("debug",True)
    objLoger = logging.getLogger('log.main')

    def normal():
        objListen = CLocalSocket()
        objListen.SetRemote(tuple_RemoteAddr)
        #objListen.setSocketClass(NORMAL_MODE)
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
        setAESEncryptionKey("0123456789abcdef")
        objListen = CLocalSocket()
        objListen.SetRemote(tuple_LocalAddrForEncryption)
        objListen.setSocketClass(CLIENT_MODE)
        objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        objListen.bind(tuple_LocalAddr)
        objListen.listen(5)
        objLoger.info ("Client Ready")

        objListen2 = CLocalSocket()
        objListen2.SetRemote(tuple_RemoteAddr)
        objListen2.setSocketClass(SERVER_MODE)
        objListen2.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        objListen2.bind(tuple_LocalAddrForEncryption)
        objListen2.listen(5)
        objLoger.info ("Server Ready")

        objSent = CBase_socket()
        objSent.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        objSent.connect(tuple_LocalAddr)
        objLoger.info ("Sent test data")
        objSent.sendData(b"test data")
        asyncore.loop(use_poll = True)

    table = [normal,encryption]

    table[index]()
