#
#
#
from Crypto.Cipher import AES

_objEncryption = None

def do16BitMultiple(szMessage):
    return do16BitMultiple_2(szMessage)

def do16BitMultiple_1(szMessage):
    length = 16 - (len(szMessage)%16)
    if length != 16:
        if type(szMessage).__name__ == "str":
            return szMessage + "\x04" + "\x00"*(length-1)
        else:
            return szMessage + b'\x04' + b'\x00'*(length-1)
    else:
        return szMessage

def do16BitMultiple_2(szMessage):
    length = 16 - (len(szMessage)%16)
    if type(szMessage).__name__ == "str":
        return szMessage + "\x04" + "\x00"*(length-1)
    else:
        return szMessage + b'\x04' + b'\x00'*(length-1)

def deleteNullChart(szMessage):
    return deleteNullChart_2(szMessage)

def deleteNullChart_1(szMessage):
    if type(szMessage).__name__ == "str":
        index = szMessage.rfind("\x04")
        #index = szMessage.find("\x00")
    else:
        index = szMessage.rfind(b'\x04')
        #index = szMessage.find(b'\x00')
    print("debug:")
    print(index)
    if (index != -1):
        return szMessage[:index]
    else: 
        return szMessage

#szMessage format which like "xxxxx\x04\x00\x00",will delete \x04\x00\x00
#else format will not change
def deleteNullChart_2(szMessage):
    if type(szMessage).__name__ != "bytes":
        raise ValueError ("type must be bytes")
    else:
        n0x04OffestFromLeft=szMessage.rfind(b'\x04')
        if len(szMessage) - n0x04OffestFromLeft > 16:
            return szMessage
        else:
            szOutput=  szMessage.rstrip(b'\x00')
            if szOutput[-1] == 0x04:
                return szOutput[:-1]
            else:#case before encode last 16byte include 0x04
                return szMessage

def setAESEncryptionKey(szKey):
    global _objEncryption
    _objEncryption = AES.new(szKey, AES.MODE_ECB)

def encrypt(szMessage):
    global _objEncryption
    if _objEncryption != None:
        return _objEncryption.encrypt(do16BitMultiple(szMessage))
#        return _objEncryption.encrypt(szMessage)
    else:
        raise AssertionError("must call setAESEncryptionKey(szkey) first")

def decrypt(szMessage):
    global _objEncryption
    if _objEncryption != None:
        print(_objEncryption.decrypt(szMessage))
        return deleteNullChart(_objEncryption.decrypt(szMessage))
#        return _objEncryption.decrypt(szMessage)
    else:
        raise AssertionError("must call setAESEncryptionKey(szkey) first")

# test case
def doTest(szTestSrt):
    sz16Multiple = do16BitMultiple(szTestSrt)
    szdelNull = deleteNullChart(sz16Multiple)
    szEncode = encrypt(szTestSrt)
    szDecode = decrypt(szEncode)

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


if __name__ == "__main__":
    setAESEncryptionKey("0123456789abcdef")
    #doTest("1")
    #doTest("17-3456789abcdef0")
    #doTest("15-asdfghjklqwe")
    #doTest("31-qwertyuiopasdfghjklzxcvbnm12")
    #doTest("16-zxcvbnm123456")
    #doTest("32-1234567890qwertyuioplkjhgfdsa")
    print("===============bytes test=====================")
    doTest(b"1")
    doTest(b"17-3456789abcdef0")
    doTest(b"15-asdfghjklqwe")
    doTest(b"31-qwertyuiopasdfghjklzxcvbnm12")
    doTest(b"16-zxcvbnm123456")
    doTest(b"32-1234567890qwertyuioplkjhgfdsa")
    print("================extend test====================")
    print(deleteNullChart(b"16-zxcvbnm123456"))
    print(deleteNullChart(b"16-zxcvbnm123\x0456"))
