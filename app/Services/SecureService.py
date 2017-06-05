from app import Globals
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
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

    def cmpHash(self, raw):
        m = hashlib.md5()
        m.update(raw)
        return m.hexdigest()

    def hash(self, raw, standard):
        standard = unicode(standard)

        if standard not in Globals.standards.hashing:
            raise ValueError('Standard unsupported')

        if standard == '0':
            return None
        elif standard == '1':
            m = hashlib.sha256()
            m.update(str(raw))
        elif standard == '3':
            m = hashlib.sha512()
            m.update(str(raw))
        
        return m.hexdigest()

    def decrypt(self, enc, standard):
        standard = unicode(standard)

        if standard not in Globals.standards.encryption:
            raise ValueError('Standard unsupported')

        if standard == '3':
            return unicode(self.privateKey.decrypt(enc))

    def encrypt(self, raw, standard, key=None):
        standard = unicode(standard)

        if standard not in Globals.standards.encryption:
            raise ValueError('Standard unsupported')

        if standard == '3':
            if key is None:
                raise TypeError('Key cannot be NoneType for this standard.')
            if len(raw) > 128:
                raise ValueError('Size of raw is bigger than 128 bytes')
            return unicode(RSA.importKey(key).encrypt(raw))

    def serverEncrypt(self, raw):
        raw = str(raw)
        raw += Globals.serverAESPadding * (Globals.serverAESBlockSize - (len(raw) % Globals.serverAESBlockSize))
        iv = Random.new().read(16)
        cipher = AES.new(Globals.serverKey, AES.MODE_CBC, iv)
        return hexlify(iv + cipher.encrypt(raw))
    
    def serverDecrypt(self, enc):
        enc = unhexlify(enc)
        iv = enc[:16]
        cipher = AES.new(Globals.serverAESPadding, AES.MODE_CBC, iv)
        return unicode(cipher.decrypt(enc[16:]).rstrip(Globals.serverAESPadding))
