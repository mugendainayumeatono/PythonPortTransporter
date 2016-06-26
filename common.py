import logging
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