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
import configparser
# user module
from common import *

dict_Config={}
dict_ConfigStr={}
dict_ConfigInt={}
dict_ConfigFloat={}
dict_ConfigBoolean={}
def init(szConfigPath):
    '''
    Red config file
    
    input the path of config file
    !!!console intput parameter will cover the parameter from config
    if no error happened return true and fill [dict_ConfigStr] [dict_ConfigInt] [dict_ConfigFloat] [dict_ConfigBoolean]
    ohterwise return False
    '''
    global dict_Config
    global dict_ConfigStr
    global dict_ConfigInt
    global dict_ConfigFloat
    global dict_ConfigBoolean
    try:
        objConfig = configparser.ConfigParser()
        objConfig.optionxform = str
        objConfig.read_file(open(szConfigPath))
    except FileNotFoundError:
        print("err:config file not found")
        return False
        
    for key in objConfig["StringParameter"]:
        dict_ConfigStr[key] = objConfig.get("StringParameter",key)
    for key in objConfig["IntegerParameter"]:
        dict_ConfigInt[key] = objConfig.getint("IntegerParameter",key)
    for key in objConfig["FloatParameter"]:
        dict_ConfigFloat[key] = objConfig.getfloat("FloatParameter",key)
    for key in objConfig["BooleanParameter"]:
        dict_ConfigBoolean[key] = objConfig.getboolean("BooleanParameter",key)
        
    if "Mode" in dict_ConfigStr:
        dict_ConfigInt["nMode"]=changeModeParameterToInteger(dict_ConfigStr["Mode"])
        del dict_ConfigStr["Mode"]
        
    dict_Config.update(dict_ConfigStr)
    dict_Config.update(dict_ConfigInt)
    dict_Config.update(dict_ConfigFloat)
    dict_Config.update(dict_ConfigBoolean)
    return True
        
        
def changeModeParameterToInteger(szMode):
    nModeFlag = 0
    if szMode == 'NORMAL_PROXY':
        nModeFlag |= NORMAL_PROXY
    elif szMode == 'ENCRYPT_CLIENT':
        nModeFlag |= ENCRYPT_CLIENT
    elif szMode == 'ENCRYPT_SERVER':
        nModeFlag |= ENCRYPT_SERVER
    else:
        print("info:Mode will be NORMAL_PROXY,ENCRYPT_CLIENT or ENCRYPT_SERVER")        
    return nModeFlag
    
if __name__ == '__main__':
    print (sys.argv[1])
    init(sys.argv[1])
    
    print ("===StringParameter===")
    for key in dict_ConfigStr:
        print ("{}:{}".format(key,dict_ConfigStr[key]))
    print ("===IntegerParameter===")
    for key in dict_ConfigInt:
        print ("{}:{}".format(key,dict_ConfigInt[key]))
    print ("===FloatParameter===")
    for key in dict_ConfigFloat:
        print ("{}:{}".format(key,dict_ConfigFloat[key]))
    print ("===BooleanParameter===")
    for key in dict_ConfigBoolean:
        print ("{}:{}".format(key,dict_ConfigBoolean[key]))
    print ("===ToalParameter===")
    for key in dict_Config:
        print ("{}:{}".format(key,dict_Config[key]))