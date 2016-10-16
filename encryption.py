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
#
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

######################################################
##AES ECB
######################################################
class AES_ecb:
    @staticmethod
    def do16BitMultiple(bytesMessage):
        return AES_ecb.do16BitMultiple_2(bytesMessage)

    @staticmethod
    def do16BitMultiple_1(bytesMessage):
        length = 16 - (len(bytesMessage)%16)
        if length != 16:
            if type(bytesMessage).__name__ == "str":
                return bytesMessage + "\x04" + "\x00"*(length-1)
            else:
                return bytesMessage + b'\x04' + b'\x00'*(length-1)
        else:
            return bytesMessage

    @staticmethod
    def do16BitMultiple_2(bytesMessage):
        length = 16 - (len(bytesMessage)%16)
        if type(bytesMessage).__name__ == "str":
            return bytesMessage + "\x04" + "\x00"*(length-1)
        else:
            return bytesMessage + b'\x04' + b'\x00'*(length-1)

    @staticmethod
    def deleteNullChart(bytesMessage):
        return AES_ecb.deleteNullChart_2(bytesMessage)

    @staticmethod
    def deleteNullChart_1(bytesMessage):
        if type(bytesMessage).__name__ == "str":
            index = bytesMessage.rfind("\x04")
            #index = bytesMessage.find("\x00")
        else:
            index = bytesMessage.rfind(b'\x04')
            #index = bytesMessage.find(b'\x00')
        if (index != -1):
            return bytesMessage[:index]
        else: 
            return bytesMessage

#bytesMessage format which like "xxxxx\x04\x00\x00",will delete \x04\x00\x00
#else format will not change
    @staticmethod
    def deleteNullChart_2(bytesMessage):
        if type(bytesMessage).__name__ != "bytes":
            raise ValueError ("type must be bytes")
        else:
            n0x04OffestFromLeft=bytesMessage.rfind(b'\x04')
            if len(bytesMessage) - n0x04OffestFromLeft > 16:
                return bytesMessage
            else:
                szOutput=  bytesMessage.rstrip(b'\x00')
                if szOutput[-1] == 0x04:
                    return szOutput[:-1]
                else:#case before encode last 16byte include 0x04
                    return bytesMessage

    def __init__(self,szKey):
        sha2 = SHA256.new(szKey.encode())
        szHashStr = sha2.hexdigest()
        self.objEncryption_AES_ECB = AES.new(szHashStr[0:32], AES.MODE_ECB)

    def encrypt(self,bytesMessage):
        if self.objEncryption_AES_ECB != None:
            return self.objEncryption_AES_ECB.encrypt(AES_ecb.do16BitMultiple(bytesMessage))
        else:
            raise AssertionError("class has not instantiation")

    def decrypt(self,bytesMessage):
        if self.objEncryption_AES_ECB != None:
            return AES_ecb.deleteNullChart(self.objEncryption_AES_ECB.decrypt(bytesMessage))
        else:
            raise AssertionError("class has not instantiation")

###########################################################################
## AES CFB
###########################################################################
class AES_cfb:
    def __init__(self,szPWD,nCFBmode = 8):
        sha2 = SHA256.new(szPWD.encode())
        szHashStr = sha2.hexdigest()
        szKey = szHashStr[0:32]
        vi = szHashStr[32:48]
        self.objEncryption_AES_CFB = AES.new(szKey, AES.MODE_CFB,vi,segment_size=nCFBmode)

    def encrypt(self,bytesMessage):
        return self.objEncryption_AES_CFB.encrypt(bytesMessage)

    def decrypt(self,bytesMessage):
        return self.objEncryption_AES_CFB.decrypt(bytesMessage)

###############################################################################
## interface
###############################################################################

_dict_mode={
    "aes-ecb":AES_ecb,
    "aes-cfb":AES_cfb
    }
_encryptor = None
_decryptor = None

def newEncryptor(mode,szPassWord):
    global _dict_mode
    if mode in _dict_mode:
        return _dict_mode[mode](szPassWord)
    else:
        raise ValueError("can not support {} mode".format(mode))
        
def setAESEncryptionKey(szPassWord,mode = "aes-cfb"):
    global _encryptor
    global _decryptor
    
    _encryptor = newEncryptor(mode,szPassWord)
    _decryptor = newEncryptor(mode,szPassWord)
    
def encrypt(bytesMessage):
    global _encryptor
    return _encryptor.encrypt(bytesMessage)

def decrypt(bytesMessage):
    global _decryptor
    return _decryptor.decrypt(bytesMessage)
# test case
def AES_ECB_Test(szTestSrt):
    objEncryptor = newEncryptor("aes-ecb","1234567890")
    sz16Multiple = objEncryptor.do16BitMultiple(szTestSrt)
    szdelNull = objEncryptor.deleteNullChart(sz16Multiple)
    szEncode = objEncryptor.encrypt(szTestSrt)
    szDecode = objEncryptor.decrypt(szEncode)

    print("=======================start==================")
    print("test srting ->{}".format(szTestSrt))
    print("16 Multiple ->{}".format(sz16Multiple))
    print("len         ->{}".format(len(sz16Multiple)))
    print("del null    ->{}".format(szdelNull))
    print("len         ->{}".format(len(szdelNull)))
    print("encode      ->{}".format(szEncode))
    print("len         ->{}".format(len(szEncode)))
    print("decode      ->{}".format(szDecode))
    print("len         ->{}".format(len(szDecode)))
    print("=====================end======================")


def AES_CFB_Test(szTestStr):
    objEncode = newEncryptor("aes-cfb","1234567890")
    objDecode = newEncryptor("aes-cfb","1234567890")
    szEncode = objEncode.encrypt(szTestStr)
    szDecode = objDecode.decrypt(szEncode)

    print("===================test encode=======================")
    print("test srting ->{}".format(szTestStr))
    print("len         ->{}".format(len(szTestStr)))
    print("encode      ->{}".format(szEncode))
    print("len         ->{}".format(len(szEncode)))
    print("decode      ->{}".format(szDecode))
    print("len         ->{}".format(len(szDecode)))

def AES_CFB_Test_Extend(szTestStr):
    objEncode = newEncryptor("aes-cfb","1234567890")
    objDecode = newEncryptor("aes-cfb","1234567890")
    szEncode = objEncode.encrypt(szTestStr)
    szDecode = objDecode.decrypt(szEncode[0:2])
    szDecode1 = objDecode.decrypt(szEncode[2:])
    print("===================test decode=======================")
    print("test srting ->{}".format(szTestStr))
    print("len         ->{}".format(len(szTestStr)))
    print("encode      ->{}".format(szEncode))
    print("len         ->{}".format(len(szEncode)))
    print("decode0     ->{}".format(szDecode))
    print("len         ->{}".format(len(szDecode)))
    print("decode1     ->{}".format(szDecode1))
    print("len         ->{}".format(len(szDecode1)))

if __name__ == "__main__":
    #doTest("1")
    #doTest("17-3456789abcdef0")
    #doTest("15-asdfghjklqwe")
    #doTest("31-qwertyuiopasdfghjklzxcvbnm12")
    #doTest("16-zxcvbnm123456")
    #doTest("32-1234567890qwertyuioplkjhgfdsa")
    print("===============ecb test=====================")
    AES_ECB_Test(b"1")
    AES_ECB_Test(b"17-3456789abcdef0")
    AES_ECB_Test(b"15-asdfghjklqwe")
    AES_ECB_Test(b"31-qwertyuiopasdfghjklzxcvbnm12")
    AES_ECB_Test(b"16-zxcvbnm123456")
    AES_ECB_Test(b"32-1234567890qwertyuioplkjhgfdsa")
    print("===============ecb test=====================")
    AES_CFB_Test(b"1")
    AES_CFB_Test(b"17-3456789abcdef0")
    AES_CFB_Test(b"15-asdfghjklqwe")
    AES_CFB_Test(b"31-qwertyuiopasdfghjklzxcvbnm12")
    AES_CFB_Test(b"16-zxcvbnm123456")
    AES_CFB_Test(b"32-1234567890qwertyuioplkjhgfdsa")
    print("================extend test====================")
    print(AES_ecb.deleteNullChart(b"16-zxcvbnm123456"))
    print(AES_ecb.deleteNullChart(b"16-zxcvbnm123\x0456"))
    AES_CFB_Test_Extend("45posld;kgn90aqwe4jkhwa")
