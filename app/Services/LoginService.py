from app import Globals
import urllib2
import hashlib
import socket

class LoginService(object):
    def __getExternalIP(self):
        return urllib2.urlopen('http://ip.42.pl/raw').read()

    def __getInternalIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        internalIP = s.getsockname()[0]
        s.close()
        return internalIP

    def loginServerStatus(self):
        return True

    def getLocation(self):
        extIP = self.__getExternalIP()

        if extIP == Globals.universityExternalIP:
            currIntIP = self.__getInternalIP()
            currIntIPArr = intIP.split('.')

            desktopIntIPArr = Globals.universityDesktop.split('.')
            wifiIntIPArr = Globals.universityWifi.split('.')
            
            if (currIntIPArr[0], currIntIPArr[1]) == (desktopIntIPArr[0], desktopIntIPArr[1]):
                return (0, currIntIP)
            elif (currIntIPArr[0], currIntIPArr[1]) == (wifiIntIPArr[0], wifiIntIPArr[1]):
                return (1, extIP)

        return (2, extIP)

    def hashPassword(self, password):
        return hashlib.sha256(password + Globals.salt).hexdigest()