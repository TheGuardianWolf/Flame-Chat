from app import Globals
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from binascii import hexlify, unhexlify

class SecureService(object):
    def __init__(self):
        self.__loadPeerKeys()

    def __loadPeerKeys(self):
        try:
            privateFile = open(Globals.privateKeyPath, 'r')
            self.privateKey = RSA.importKey(privateFile.read())
            privateFile.close()
            print 'Using private key found at ' + Globals.privateKeyPath

            try:
                publicFile = open(Globals.publicKeyPath, 'r')
                self.publicKey = RSA.importKey(publicFile.read())
                publicFile.close()
                print 'Using public key found at ' + Globals.publicKeyPath
            except:
                self.publicKey = self.privateKey.publickey()
                privateFile = open(Globals.privateKeyPath, 'w')
                privateFile.write(self.privateKey.exportKey("PEM"))
                privateFile.close()
                print 'Created new public key at ' + Globals.publicKeyPath
        except:
            self.privateKey = RSA.generate(1024, e=65537)
            self.publicKey = self.privateKey.publickey()

            publicFile = open(Globals.publicKeyPath, 'w')
            publicFile.write(self.publicKey.exportKey('PEM') )
            publicFile.close()
            print 'Created new private key at ' + Globals.privateKeyPath

            privateFile = open(Globals.privateKeyPath, 'w')
            privateFile.write(self.privateKey.exportKey('PEM'))
            privateFile.close()
            print 'Created new public key at ' + Globals.publicKeyPath

    def encryptWithKey(self, key, raw):
        return RSA.importKey(key).encrypt(raw)

    def serverEncrypt(self, raw):
        raw += Globals.serverAESPadding * (Globals.serverAESBlockSize - (len(raw) % Globals.serverAESBlockSize))
        iv = Random.new().read(16)
        cipher = AES.new(Globals.serverKey, AES.MODE_CBC, iv)
        return hexlify(iv + cipher.encrypt(raw))
    
    def serverDecrypt(self, enc):
        enc = unhexlify(enc)
        iv = enc[:16]
        cipher = AES.new(Globals.serverAESPadding, AES.MODE_CBC, iv)
        return cipher.decrypt(enc[16:]).rstrip(Globals.serverAESPadding)
