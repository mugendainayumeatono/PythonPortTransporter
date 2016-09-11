import logging

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