from app import Globals
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
from binascii import hexlify, unhexlify

class SecureService(object):
    """
    Manages encryption and hashing.
    """
    def __init__(self, privateKeyPath, publicKeyPath):
        self.__loadPeerKeys(privateKeyPath, publicKeyPath)

    def __loadPeerKeys(self, privateKeyPath, publicKeyPath):
        try:
            privateFile = open(privateKeyPath, 'r')
            self.privateKey = RSA.importKey(privateFile.read())
            privateFile.close()
            print 'Using private key found at ' + privateKeyPath

            try:
                publicFile = open(publicKeyPath, 'r')
                self.publicKey = RSA.importKey(publicFile.read())
                publicFile.close()
                print 'Using public key found at ' + publicKeyPath
            except:
                self.publicKey = self.privateKey.publickey()
                privateFile = open(privateKeyPath, 'w')
                privateFile.write(self.privateKey.exportKey("PEM"))
                privateFile.close()
                print 'Created new public key at ' + publicKeyPath
        except:
            self.privateKey = RSA.generate(1024, e=65537)
            self.publicKey = self.privateKey.publickey()

            publicFile = open(publicKeyPath, 'w')
            publicFile.write(self.publicKey.exportKey('PEM'))
            publicFile.close()
            print 'Created new private key at ' + privateKeyPath

            privateFile = open(privateKeyPath, 'w')
            privateFile.write(self.privateKey.exportKey('PEM'))
            privateFile.close()
            print 'Created new public key at ' + publicKeyPath

    def cmpHash(self, raw):
        m = hashlib.md5()
        m.update(unicode(raw))
        return m.hexdigest()

    def hash(self, raw, standard):
        raw = str(unicode(raw).encode('utf-8'))
        standard = unicode(standard)

        if standard not in Globals.standards['hashing']:
            raise ValueError('Standard unsupported')

        if standard == '0':
            return None
        elif standard == '1':
            m = hashlib.sha256()
            m.update(raw)
        elif standard == '3':
            m = hashlib.sha512()
            m.update(raw)
        
        return m.hexdigest()

    def decrypt(self, enc, standard):
        standard = unicode(standard)

        if standard not in Globals.standards['encryption']:
            raise ValueError('Standard unsupported')

        if standard == '3':
            return unicode(self.privateKey.decrypt(unhexlify(enc)))

    def encrypt(self, raw, standard, key=None):
        standard = unicode(standard)
        raw = str(unicode(raw).encode('utf-8'))

        if standard not in Globals.standards['encryption']:
            raise ValueError('Standard unsupported')

        if standard == '3':
            if key is None:
                raise TypeError('Key cannot be NoneType for this standard.')
            pubKey = RSA.importKey(unhexlify(key))
            return unicode(hexlify(pubKey.encrypt(raw, Random.new().read(16))[0]))

    def serverEncrypt(self, raw):
        raw = str(unicode(raw).encode('utf-8'))
        raw += Globals.serverAESPadding * (Globals.serverAESBlockSize - (len(raw) % Globals.serverAESBlockSize))
        iv = Random.new().read(16)
        cipher = AES.new(Globals.serverKey, AES.MODE_CBC, iv)
        return unicode(hexlify(iv + cipher.encrypt(raw)))
    
    def serverDecrypt(self, enc):
        enc = unhexlify(enc)
        iv = enc[:16]
        cipher = AES.new(Globals.serverAESPadding, AES.MODE_CBC, iv)
        return unicode(cipher.decrypt(enc[16:]).rstrip(Globals.serverAESPadding))
