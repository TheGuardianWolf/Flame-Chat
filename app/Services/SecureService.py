import Globals
from Crypto.PublicKey import RSA

class SecureService():
    def __init__(self):
        self.__loadPeerKeys__()
        self.__loadServerKeys__()

    def __loadPeerKeys__(self):
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
            publicFile.write(self.publicKey.exportKey("PEM") )
            publicFile.close()
            print 'Created new private key at ' + Globals.privateKeyPath

            privateFile = open(Globals.privateKeyPath, 'w')
            privateFile.write(self.privateKey.exportKey("PEM"))
            privateFile.close()
            print 'Created new public key at ' + Globals.publicKeyPath

    def __loadServerKeys__(self):
        self.serverKey = AES.new(Globals.serverKey, AES.MODE_CBC, binascii.unhexlify(enc)[:16])