import cherrypy
from datetime import datetime
from binascii import hexlify
from time import sleep
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.AuthModel import Auth

class AuthController(__Controller):
    def __init__(self, services):
        super(AuthController, self).__init__(services)

    def __localAuth(self, username, passhash):
        auth = self.DS.select(Auth, 'username=' + username)
        if auth is not None and auth.username == username and auth.passhash == passhash:
            cherrypy.session['authenticated'] = True
            cherrypy.session['username'] = username
            cherrypy.session['passhash'] = passhash
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
            'pubkey': hexlify(self.SS.publicKey.exportKey('DER'))
        }

        if enc > 0:
            for key in payload.keys():
                payload[key] = self.SS.serverEncrypt(payload[key])

            payload['enc'] = 1

        (status, response) = self.RS.get(Globals.loginRoot, '/report', payload)

        if response is not None:
            (errorCode, errorMessage) = response.read().split(',')

            errorCode = int(errorCode)
            
            if errorCode ==  6 and payload['enc'] == 1:
                raise Exception((errorCode, errorMessage))
                (errorCode, errorMessage) = self.__loginServerAuth(username, passhash, enc=0)
                errorCode = int(errorCode)

            return (errorCode, errorMessage)
        else:
            return (-2, 'Request error ' + str(status) + ': Login server authentication not available.')

    def dynamicAuth(self, username, passhash, enc=1, sessionData=None):
        if sessionData is None:
            cherrypy.session['lastLoginReportTime'] = datetime.utcnow()
        else:
            sessionData['lastLoginReportTime'] = datetime.utcnow()

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
            else:
                cherrypy.session['authenticated'] = False
        else:
            (errorCode, errorMessage) = self.__localAuth(username, passhash)
            errorMessage += ' Login server offline or unreachable.'

        if cherrypy.session['authenticated'] == True:
            try:
                if (self.MS.data['authenticatedUsers'].count(username) == 0):
                    self.MS.data['authenticatedUsers'].append(username)
            except KeyError:
                self.MS.data['authenticatedUsers'] = [username]

        return (errorCode, errorMessage)

    def __storeAuth(self, username, passhash):
        q = self.DS.select(Auth, 'username=' + self.DS.queryFormat(username))

        if q is not None and len(q) > 0:
            q = q[0]
            if not q.passhash == passhash:
                self.DS.update(Auth(q.id, q.username, passhash), 'id='+ self.DS.queryFormat(id))
        else:
            self.DS.insert(Auth(None, username, passhash))

    def dynamicLogoff(self, username, passhash, enc=1):
        if (self.LS.online):
            payload = {
                'username': username,
                'password': passhash
            }

            if enc > 0:
                for key in payload.keys():
                        payload[key] = self.SS.serverEncrypt(payload[key])
                payload['enc'] = 1

            (status, response) = self.RS.get(Globals.loginRoot, '/logoff', payload)

            if response is not None:
                (errorCode, errorMessage) = response.read().split(',')

                errorCode = int(errorCode)
            
                if errorCode ==  6 and payload['enc'] == 1:
                    raise Exception((errorCode, errorMessage))
                    (errorCode, errorMessage) = self.dynamicLogoff(username, passhash, enc=0)
                    errorCode = int(errorCode)

                return (errorCode, errorMessage)
            else:
                return (-2, 'Request error ' + str(status) + ': Login server authentication not available.')
        else:
            return (-1, 'Login server is offline.')

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def login(self):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')

        try:
            request = cherrypy.request.json
        except AttributeError:
            raise cherrypy.HTTPError(400, 'JSON payload not sent.')

        if not self.checkObjectKeys(request, ['username', 'password']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')
        
        username = request['username']
        password = request['password']
        passhash = self.LS.hashPassword(password)
        (errorCode, errorMessage) = self.dynamicAuth(username, passhash)
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return unicode(errorCode)

    @cherrypy.expose
    def logoff(self):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        (errorCode, errorMessage) = self.dynamicLogoff(cherrypy.session['username'], cherrypy.session['passhash'])
        del cherrypy.session['pulled']
        del cherrypy.session['lastLoginReportTime']
        del cherrypy.session['streamEnabled']
        
        return unicode(errorCode)
