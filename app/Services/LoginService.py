import Globals
import urllib2

class LoginService():
    def __init__(self):
        pass

    def findLocation():
        externalIP = urllib2.urlopen('http://ip.42.pl/raw').read()
        return externalIP