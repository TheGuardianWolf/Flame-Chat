import cherrypy
from datetime import datetime
import Globals
from app.Models.AuthModel import Auth

class AuthController(object):
    def __init__(self, services):
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RestfulService']
        self.DS = services['DatabaseService']

    def __isAuthenticated(self):
        if ('authenticated' not in cherrypy.session or cherrypy.session['authenticated'] == False):
            return False
        return True

    def __localAuth(self, username, passhash):
        pass

    def __loginServerAuth(self, username, passhash, enc=1):
        (location, ip) = self.LS.getLocation()

        payload = {
            'username': username,
            'password': passhash,
            'location': location,
            'ip': ip,
            'port': Globals.publicPort,
            'pubkey': self.SS.publicKey.exportKey('PEM')
        }

        if enc > 0:
            for key in payload.keys():
                payload[key] = self.SS.serverEncrypt(str(payload[key]))

            payload['enc'] = 1

        (status, response) = self.RS.get(Globals.loginRoot, '/report', payload)

        if response is not Null:
            (errorCode, errorMessage) = response.read().split(',')

            errorCode = int(errorCode)

            if errorCode ==  6:
                (errorCode, errorMessage) = self.__loginServerAuth(username, passhash, enc=0)
                errorCode = int(errorCode)

            return (errorCode, errorMessage)
        else:
            return (-2, 'Request error ' + str(errorCode) + ': Login server authentication not available.')

    def __dynamicAuth(self, username, passhash, enc=1):
        (errorcode, errorMessage) = self.__loginServerAuth(username, passhash)

        if errorCode == 0:
            cherrypy.session['authenticated'] = True
            cherrypy.session['username'] = username
            cherrypy.session['passhash'] = passhash
            cherrypy.session['lastReportTime'] = datetime.now()
            self.DS.insert(Auth(None, username, passhash))
        else:
            cherrypy.session['authenticated'] = False

        return (errorCode, errorMessage)

    @cherrypy.expose
    def stream(self):
        if not self.__isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        cherrypy.response.headers['Content-Type'] = 'text/event-stream;charset=utf-8'
        errorCode = '-1'
        
        if (datetime.now() - cherrypy.session['lastReportTime']).seconds > 40:
            (errorCode, errorMessage) = self.__dynamicAuth(cherrypy.session['username'], cherrypy.session['passhash'])

        return str(errorCode) + '\n\n'

    '''
    Using the local api requires login
    '''
    @cherrypy.expose
    def login(self, username, password):
        passhash = self.LS.hashPassword(password)
        (errorCode, errorMessage) = self.__dynamicAuth(username, passhash)
        return str(errorCode)

    @cherrypy.expose
    def getUsers(self, username, password, enc=1):
        if not self.__isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        payload = {
            'username': cherrypy.session['username'],
            'password': cherrypy.session['passhash']
        }

        if enc > 0:
            for key in payload.keys():
                payload[key] = self.SS.serverEncrypt(str(payload[key]))

        (status, response) = self.RS.get(Globals.loginRoot, '/getList', payload)
