import cherrypy
from datetime import datetime
from app import Globals
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
        auth = self.DS.select(Auth, 'username=' + username)
        if auth is not None and auth.username == username and auth.passhash == passhash:
            cherrypy.session['authenticated'] = True
            cherrypy.session['username'] = username
            cherrypy.session['passhash'] = passhash
            cherrypy.session['lastReportTime'] = datetime.now()
            return (-1, 'Locally verified.')
        else:
            cherrypy.session['authenticated'] = False
            return (-2, 'Cannot locally verify.')

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

        if response is not None:
            (errorCode, errorMessage) = response.read().split(',')

            errorCode = int(errorCode)

            if errorCode ==  6 and payload['enc'] == 1:
                (errorCode, errorMessage) = self.__loginServerAuth(username, passhash, enc=0)
                errorCode = int(errorCode)

            return (errorCode, errorMessage)
        else:
            return (-2, 'Request error ' + str(status) + ': Login server authentication not available.')

    def __dynamicAuth(self, username, passhash, enc=1):
        if (self.LS.loginServerStatus()):
            (errorCode, errorMessage) = self.__loginServerAuth(username, passhash)

            if errorCode == 0:
                cherrypy.session['authenticated'] = True
                cherrypy.session['username'] = username
                cherrypy.session['passhash'] = passhash
                self.__storeAuth(username, passhash)
            elif errorCode == -2:
                (errorCode, errorMessage) = self.__localAuth(username, passhash)
                errorMessage += ' Request to login server failed with unhandled error.'
                return (errorCode, errorMessage)
            else:
                cherrypy.session['authenticated'] = False

            cherrypy.session['lastLoginReportTime'] = datetime.now()
            return (errorCode, errorMessage)
        else:
            (errorCode, errorMessage) = self.__localAuth(username, passhash)
            errorMessage += ' Login server offline or unreachable.'
            cherrypy.session['lastLoginReportTime'] = datetime.now()
            return (errorCode, errorMessage)

    def __storeAuth(self, username, passhash):
        q = self.DS.select(Auth, 'username=' + self.DS.queryFormat(username))

        if q is not None:
            q = q[0]
            if not q.passhash == passhash:
                self.DS.update(Auth(q.id, q.username, passhash), 'id='+ self.DS.queryFormat(id))
        else:
            self.DS.insert(Auth(None, username, passhash))

    @cherrypy.expose
    def stream(self):
        if not self.__isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        cherrypy.response.headers['Content-Type'] = 'text/event-stream;charset=utf-8'
        errorCode = '-1'
        
        if (datetime.now() - cherrypy.session['lastLoginReportTime']).seconds > 40:
            (errorCode, errorMessage) = self.__dynamicAuth(cherrypy.session['username'], cherrypy.session['passhash'])

        return str(errorCode) + errorMessage + '\n\n'

    @cherrypy.expose
    def login(self, username, password):
        passhash = self.LS.hashPassword(password)
        (errorCode, errorMessage) = self.__dynamicAuth(username, passhash)
        return str(errorCode)
