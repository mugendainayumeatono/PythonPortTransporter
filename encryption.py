#判断 传入的是什么类型
#已经传出时类型是否改变
#
#
from Crypto.Cipher import AES

_objEncryption = None

def do16BitMultiple(szMessage):
    length = 16 - (len(szMessage)%16)
    if length != 16:
        if type(szMessage).__name__ == "str":
            return szMessage + "\0"*length
        else:
            return szMessage + b'\0'*length
    else:
        return szMessage

def deleteNullChart(szMessage):
    if type(szMessage).__name__ == "str":
        return szMessage.rstrip("\0")
    else:
        return szMessage.rstrip(b'\0')

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
        return deleteNullChart(_objEncryption.decrypt(szMessage))
#        return _objEncryption.decrypt(szMessage)
    else:
        raise AssertionError("must call setAESEncryptionKey(szkey) first")

if __name__ == "__main__":
    try:
        print(encrypt("szMessage"))
    except Exception:
        setAESEncryptionKey("0123456789abcdef")
        szString = encrypt("1")
        print(szString)
        print(decrypt(szString))
        print(len(decrypt(szString)))

        szString = encrypt("17-3456789abcdef0")
        print(szString)
        print(decrypt(szString))
        print(len(decrypt(szString)))

        szString = encrypt("15-asdfghjklqwe")
        print(szString)
        print(decrypt(szString))
        print(len(decrypt(szString)))

        szString = encrypt("31-qwertyuiopasdfghjklzxcvbnm12")
        print(szString)
        print(decrypt(szString))
        print(len(decrypt(szString)))

        szString = encrypt(b"16-zxcvbnm123456")
        print(szString)
        print(decrypt(szString))
        print(len(decrypt(szString)))

        szString = encrypt(b"32-1234567890qwertyuioplkjhgfdsa")
        print(szString)
        print(decrypt(szString))
        print(len(decrypt(szString)))
        
        szMessage = b'start\0\0\0\0'
        szMessage.rstrip(b"\0")
        print(szMessage)
        print(do16BitMultiple("abc"))
        print(do16BitMultiple(b"def"))
        print(deleteNullChart("abc\0\0\0\0"))
        print(deleteNullChart(b"start\0\0\0\0"))