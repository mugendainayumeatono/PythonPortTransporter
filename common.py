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

import logging

############### global set ############
ENCRYPTION_MODE = "aes-cfb"
################# macro ###############
NORMAL_MODE = 0
SERVER_MODE = 1
CLIENT_MODE = 2

NORMAL_PROXY =     0b00000001
SERVER_PEER =        0b00000010
CLIENT_PRRR =         0b00000100
ENCRYPTION =          0b00001000
CONTRARY_PROXY = 0b00010000
ENCRYPT_SERVER =  SERVER_PEER | ENCRYPTION
ENCRYPT_CLIENT =   CLIENT_PRRR | ENCRYPTION
NORMAL_CONTRARY = CONTRARY_PROXY | NORMAL_PROXY
CONTRARY_SERVER = CONTRARY_PROXY | ENCRYPT_SERVER
CONTRARY_CLIENT =  CONTRARY_PROXY | ENCRYPT_CLIENT

dict_LogLevel = {
    "debug":logging.DEBUG,
    "info":logging.INFO,
    "warning":logging.WARNING,
    "error":logging.ERROR
}
szLogPath = "log"
def globefunStartLog(LogLevel = "info",bConsole = False):
    szLogRecord = "%(asctime)s PID:%(process)d  In module:%(module)s[%(name)s] %(funcName)s() %(lineno)d %(levelname)s: %(message)s"
    objFormatter = logging.Formatter(szLogRecord)
  
    objFileHander = logging.FileHandler(szLogPath)
    objFileHander.setFormatter(objFormatter)
  
    objStreamHandler = logging.StreamHandler()
    objStreamHandler.setFormatter(objFormatter)

    objLoger = logging.getLogger('log')
    objLoger.addHandler(objFileHander)
    if bConsole:
        objLoger.addHandler(objStreamHandler)

    objLoger.setLevel(dict_LogLevel[LogLevel])

if __name__=='__main__':
    loglevel = "info"
    objMainLoger = logging.getLogger('log.main')
    globefunStartLog(loglevel,True)
    print("log level = {}".format(loglevel))
    objMainLoger.info("info")
    objMainLoger.debug("debug")
    objMainLoger.warning("warning")
    objMainLoger.error("error")

