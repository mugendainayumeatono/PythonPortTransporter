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
import configparser
# user module
from common import *
from service import *

objMainLoger = None

def usage():
    print("-n        normal proxy,local will connect to remote(NORMAL_PROXY)")
    print("-c        start as client peer connection will encrypt(ENCRYPT_CLIENT)")
    print("-s        start as server peer connection will encrypt(ENCRYPT_SERVER)")
    print("-C        upper case -C,Contrary proxy,remote will connect to local, this is ues for cross local NAT")
    print("-d        debug")
    print("--key     encryption keyword,lenght must 16 byte")
    print("--ip      set remote ip adderss")
    print("--lport   set local port")
    print("--rport   set remote port")
    
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
    szloglevel = "info"
    nFlag = 0
    szConfigPath = "config"
    global objMainLoger
    if len(sys.argv) <= 1:
        usage()
        sys.exit(2)
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ncsC:hd",["ip=","lport=","rport=","key="])
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
        elif eachOpt == "-C":
            try:
                szConfigPath = str(eachArg)
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
        elif eachOpt == "-d":
            szloglevel = "debug"
        elif eachOpt == "-h":
            usage()
            sys.exit()
        else:
            print("err:unknow option {}".format(eachOpt))
            usage()
            sys.exit(2)
           

    objMainLoger = logging.getLogger('log.main')
    globefunStartLog(szloglevel,True)
        
    try:
    #if 'szConfigPath' in locals():
        objConfig = configparser.ConfigParser()
        objConfig.read_file(open(szConfigPath))
        #objConfig.read(szConfigPath)        
        try:
            nListenPort=objConfig.getint('config','ListenPort')
        except configparser.NoOptionError:
            print("info:ListenPort has not define in config section")
        try:
            szForwardIP=objConfig.get('config','ForwardIP')
        except configparser.NoOptionError:
            print("info:ForwardIP has not define in config section")
        try:
            nForwardPort=objConfig.getint('config','ForwardPort')
        except configparser.NoOptionError:
            print("info:ForwardPort has not define in config section")
        try:
            szEncryptionKey=objConfig.get('config','EncryptionKey')
        except configparser.NoOptionError:
            print("info:EncryptionKey has not define in config section")
        try:
            szMode=objConfig.get('config','Mode')
            nModeFlag = 0
            if szMode == 'NORMAL_PROXY':
                nModeFlag |= NORMAL_PROXY
            elif szMode == 'ENCRYPT_CLIENT':
                nModeFlag |= ENCRYPT_CLIENT
            elif szMode == 'ENCRYPT_SERVER':
                nModeFlag |= ENCRYPT_SERVER
            else:
                print("info:Mode will be NORMAL_PROXY,ENCRYPT_CLIENT or ENCRYPT_SERVER")
        except configparser.NoOptionError:
            print("info:Mode has not define in config section")
    except FileNotFoundError:
        print("info:config file not found")
        
    #check param
    if "nLocalPort" not in locals():
        if "nListenPort" in locals():
            nLocalPort=nListenPort
        else:
            print("err:must specify local port")
            sys.exit(2)
    if "szRemoteIP" not in locals():
        if "szForwardIP" in locals():
            szRemoteIP=szForwardIP
        else:
            print("err:must specify remote ip")
            sys.exit(2)
    if "nRemotePort" not in locals():
        if "nForwardPort" in locals():
            nRemotePort=nForwardPort
        else:
            print("err:must specify remote port")
            sys.exit(2)
    if nFlag ==0:
        if "szMode" in locals():
            nFlag = nModeFlag
        else:
            print("err:must specify a mode")
            sys.exit(2)
    if (nFlag & ENCRYPTION) != 0:
        if "szKey" not in locals():
            if "szEncryptionKey" in locals():
                szKey = szEncryptionKey
            else:
                print("err:must specify a key")
                sys.exit(2)

    objMainLoger.info("start at {}".format(time.asctime()))
    if nFlag == NORMAL_PROXY:
        objMainLoger.debug("nLocalPort {}".format(nLocalPort))
        objMainLoger.debug("szRemoteIP {}".format(szRemoteIP))
        objMainLoger.debug("nRemotePort {}".format(nRemotePort))
        #startService(nLocalPort,szRemoteIP,nRemotePort)
    elif nFlag == ENCRYPT_CLIENT:
        objMainLoger.debug("nLocalPort {}".format(nLocalPort))
        objMainLoger.debug("szRemoteIP {}".format(szRemoteIP))
        objMainLoger.debug("nRemotePort {}".format(nRemotePort))
        objMainLoger.debug("szKey {}".format(szKey))
        #startEncryptionService_AsClient(nLocalPort,szRemoteIP,nRemotePort,szKey)
    elif nFlag == ENCRYPT_SERVER:
        objMainLoger.debug("nLocalPort {}".format(nLocalPort))
        objMainLoger.debug("szRemoteIP {}".format(szRemoteIP))
        objMainLoger.debug("nRemotePort {}".format(nRemotePort))
        objMainLoger.debug("szKey {}".format(szKey))
        #startEncryptionService_AsServer(nLocalPort,szRemoteIP,nRemotePort,szKey)
    else:
        print("err:must chose one and only one mode")
        sys.exit(2)
        
    
    
if __name__ == '__main__' :
    main()
