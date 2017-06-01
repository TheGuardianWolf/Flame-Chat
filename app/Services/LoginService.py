import Globals
import urllib2
import hashlib

class LoginService(object):
    def __init__(self):
        pass

    def findLocation(self):
        return 2

    def getIP(self):
        externalIP = urllib2.urlopen('http://ip.42.pl/raw').read()
        return externalIP

    def getPassword(self):
        return hashlib.sha256( + Globals.salt).hexdigest()