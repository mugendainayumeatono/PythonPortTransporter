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
import os
import logging
import getopt
import sys
import time
# user module
from common import *
from service import *
import config

objMainLoger = None

def usage():
    print("-n         normal proxy,local will connect to remote(NORMAL_PROXY)")
    print("-c         start as client peer connection will encrypt(ENCRYPT_CLIENT)")
    print("-s         start as server peer connection will encrypt(ENCRYPT_SERVER)")
    #print("-C        upper case -C,Contrary proxy,remote will connect to local, this is ues for cross local NAT")
    print("--debug    debug")
    print("--key      encryption keyword,lenght must 16 byte")
    print("--ip       set remote ip adderss")
    print("--lport    set local port")
    print("--rport    set remote port")
    print("--config   use config file !!console intput parameter will cover the parameter from config  ")
    
def startService(nLocalPort,szRemoteIP,nRemotePort):
    global objMainLoger
    tuple_RemoteAddr = (szRemoteIP,nRemotePort)
    tuple_LocalAddr = ("",nLocalPort)
    
    objListen = CLocalSocket()
    objListen.selfConfigure(tuple_RemoteAddr,NORMAL_MODE)
    objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objListen.bind(tuple_LocalAddr)
    objListen.listen(5)
    try:
        asyncore.loop(use_poll = True)
    except OSError as why:
        objMainLoger.error(why)
        traceback_error(objMainLoger)
        asyncore.loop(use_poll = True)
        
def startEncryptionService_AsClient(nLocalPort,szRemoteIP,nRemotePort,szKey):
    global objMainLoger
    tuple_RemoteAddr = (szRemoteIP,nRemotePort)
    tuple_LocalAddr = ("",nLocalPort)

    objListen = CLocalSocket()
    objListen.selfConfigure(tuple_RemoteAddr,CLIENT_MODE,szKey)
    objListen.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objListen.bind(tuple_LocalAddr)
    objListen.listen(5)
    try:
        asyncore.loop(use_poll = True)
    except OSError as why:
        objMainLoger.error(why)
        traceback_error(objMainLoger)
        asyncore.loop(use_poll = True)

def startEncryptionService_AsServer(nLocalPort,szRemoteIP,nRemotePort,szKey):
    global objMainLoger
    tuple_RemoteAddr = (szRemoteIP,nRemotePort)
    tuple_LocalAddr = ("",nLocalPort)

    objListen2 = CLocalSocket()
    objListen2.selfConfigure(tuple_RemoteAddr,SERVER_MODE,szKey)
    objListen2.create_socket(socket.AF_INET,socket.SOCK_STREAM)
    objListen2.bind(tuple_LocalAddr)
    objListen2.listen(5)
    try:
        asyncore.loop(use_poll = True)
    except OSError as why:
        objMainLoger.error(why)
        traceback_error(objMainLoger)
        asyncore.loop(use_poll = True)


def main():
    nFlag = 0
    bHasconfig = False
    global objMainLoger
    if len(sys.argv) <= 1:
        usage()
        sys.exit(2)
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ncsC:hd",["ip=","lport=","rport=","key=","config=","debug"])
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
                print("err:ip must be a string")
                sys.exit(2)
        elif eachOpt == "--lport":
            try:
                nLocalPort = int(eachArg)
            except ValueError:
                print("err:potr must be a number")
                sys.exit(2)
        elif eachOpt == "--rport":
            try:
                nRemotePort = int(eachArg)
            except ValueError:
                print("err:potr must be a number")
                sys.exit(2)
        elif eachOpt == "--config":
            try:
                szConfigPath = str(eachArg)
                bHasconfig = True
            except ValueError:
                print("err:config file Path must be a string")
                sys.exit(2)
        elif eachOpt == "--key":
            szKey = eachArg
        elif eachOpt == "-n":
            nFlag = nFlag | NORMAL_PROXY
        elif eachOpt == "-c":
            nFlag = nFlag | ENCRYPT_CLIENT
        elif eachOpt == "-s":
            nFlag = nFlag | ENCRYPT_SERVER
        elif eachOpt == "--debug":
            szloglevel = "debug"
        elif eachOpt == "-h":
            usage()
            sys.exit()
        else:
            print("err:unknow option {}".format(eachOpt))
            usage()
            sys.exit(2)
        
    if bHasconfig:
        if not config.init(szConfigPath):
            print("err:load config file fail")
            sys.exit(2)
        
    #parameter check
    #console intput parameter will cover the parameter from config 
    if "nLocalPort" in locals():
        config.dict_Config["ListenPort"] = nLocalPort
    if "ListenPort" not in config.dict_Config:
        print("err:must specify local port")
        sys.exit(2)
    if "szRemoteIP" in locals():
        config.dict_Config["ForwardIP"] = szRemoteIP
    if "ForwardIP" not in config.dict_Config:
        print("err:must specify remote ip")
        sys.exit(2)
    if "nRemotePort" in locals():
        config.dict_Config["ForwardPort"] = nRemotePort
    if "ForwardPort" not in config.dict_Config:
        print("err:must specify remote port")
        sys.exit(2)
    if nFlag != 0:
        config.dict_Config["nMode"] = nFlag
    if "nMode" not in config.dict_Config:
        print("err:must specify  a mode")
        sys.exit(2)
    if "szKey" in locals():
        config.dict_Config["EncryptionKey"] = szKey
    if (config.dict_Config["nMode"] & ENCRYPTION) != 0:
        if "EncryptionKey" not in config.dict_Config:
            print("err:must specify a key")
            sys.exit(2)
    if "szloglevel" in locals():
        config.dict_Config["LogLevel"]=szloglevel
    if "LogLevel" not in config.dict_Config:
        config.dict_Config["LogLevel"]="debug"
    if "LogPath" not in config.dict_Config:
        config.dict_Config["LogPath"]="log"
            
    objMainLoger = logging.getLogger('log.main')
    globefunStartLog(config.dict_Config["LogPath"],config.dict_Config["LogLevel"],False)
    
    objMainLoger.info("start at {}".format(time.asctime()))   
            
    objMainLoger.debug ("===Parameter List===")
    for param in config.dict_Config:
        objMainLoger.debug ("{}:{}".format(param,config.dict_Config[param]))   
        
    if config.dict_Config["nMode"] == NORMAL_PROXY:
        objMainLoger.debug("proxy mode:NORMAL_PROXY")
        startService(config.dict_Config["ListenPort"],config.dict_Config["ForwardIP"],config.dict_Config["ForwardPort"])
    elif config.dict_Config["nMode"] == ENCRYPT_CLIENT:
        objMainLoger.debug("proxy mode:ENCRYPT_CLIENT")
        startEncryptionService_AsClient(config.dict_Config["ListenPort"],config.dict_Config["ForwardIP"],config.dict_Config["ForwardPort"],config.dict_Config["EncryptionKey"])
    elif config.dict_Config["nMode"] == ENCRYPT_SERVER:
        objMainLoger.debug("proxy mode:ENCRYPT_SERVER ")
        startEncryptionService_AsServer(config.dict_Config["ListenPort"],config.dict_Config["ForwardIP"],config.dict_Config["ForwardPort"],config.dict_Config["EncryptionKey"])
    else:
        print("err:must chose one and only one mode")
        sys.exit(2)
        
    
    
if __name__ == '__main__' :
    main()
