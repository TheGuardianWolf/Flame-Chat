import cherrypy
from datetime import datetime
from json import loads, dumps
from binascii import hexlify
from os import path
from app import Globals
from app.Controllers import __Controller
from app.Models.AuthModel import Auth
from app.Models.MessageModel import Message
from app.Models.UserModel import User
from app.Models.ProfileModel import Profile
from app.Models.FileModel import File

class PublicController(__Controller):
    _cp_config = {
        'tools.sessions.on': False
    }

    encoding = ['0', '2']
    encryption = ['0', '3', '4']
    hashing = ['0', '1', '2', '3', '4']

    def __init__(self, services):
        super(PublicController, self).__init__(services)

        f = open(path.join(Globals.appConfigRoot, 'publicAPI.json'))
        self.apiList = loads(f.read())
        f.close()

        f = open(path.join(Globals.appConfigRoot, 'blacklist.json'))
        self.blacklist = loads(f.read())
        f.close()

    def __userFilter(self, ip):
        return True

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPError(403, 'You don\'t have permission to access / on this server.')
    
    @cherrypy.expose
    def listAPI(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        output = [
            '\n'.join(self.apiList),
            'Encoding ' + ' '.join(self.encoding),
            'Encryption ' + ' '.join(self.encryption),
            'Hashing ' + ' '.join(self.hashing)
        ]

        return '\n'.join(output)

    @cherrypy.expose
    def ping(self, sender):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'
        return '0'

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def recieveMessage(self, encoding='0'):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.RS.checkObjectKeys(self, request, ['sender', 'destination', 'message', 'stamp']):
            return '1'

        request['encoding'] = unicode(encoding)

        msg = Message.deserialize(request)

        self.DS.insert(msg)
        return '0'
        
    @cherrypy.tools.json_in()
    @cherrypy.expose
    def acknowledge(self):
        raise cherrypy.HTTPError(404, 'Not implemented.')

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getPublicKey(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.RS.checkObjectKeys(self, request, ['sender', 'profile_username']):
            return '1'

        responseObj = {}

        responseObj['error'] = 0
        responseObj['pubKey'] = hexlify(self.SS.publicKey.exportKey('DER'))

        cherrypy.response.headers['Content-Type'] = 'application/json'
        return dumps(responseObj)

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def handshake(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.RS.checkObjectKeys(self, request, ['sender', 'destination', 'message', 'encryption']):
            return '1'

        if self.encryption.count(str(request['encryption'])) == 0:
            return '9'

        responseObj = {}

        responseObj['error'] = 0
        responseObj['message'] = self.SS.privateKey.decrypt(request['message'])

        cherrypy.response.headers['Content-Type'] = 'application/json'
        return dumps(responseObj)

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getProfile(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json
        try:
            username = request['profile_username']
        except KeyError:
            return '1'

        try:
            user = self.DS.select(User, 'username=' + self.DS.queryFormat(username))[0]
            profile = self.DS.select(Profile, 'userId=' + self.DS.queryFormat(user.id))[0]
        except IndexError:
            return '4'

        profileObj = profile.serialize()
        del profileObj['id']
        del profileObj['userId']
        profileObj['encoding'] = 0

        cherrypy.response.headers['Content-Type'] = 'application/json'
         
        if user.publicKey is not None:
            encProfileObj = {}
            try:
                for key, value in profileObj.items():
                    encProfileObj[key] = self.SS.encryptWithKey(user.publicKey, unicode(value).encode('ascii', errors='replace'))
                encProfileObj['encryption'] = 3
                return dumps(profileObj)
            except ValueError:
                pass

        return dumps(profileObj)
    
    @cherrypy.tools.json_in()
    @cherrypy.expose
    def recieveFile(self, encoding):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.RS.checkObjectKeys(self, request, ['sender', 'destination', 'file', 'filename', 'content_type', 'stamp', 'hashing']):
            return '1'

        request['encoding'] = unicode(encoding)

        f = File.deserialize(request)

        self.DS.insert(f)
        return '0'

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def retrieveMessages(self):
        raise cherrypy.HTTPError(404, 'Not implemented.')

        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.RS.checkObjectKeys(self, request, ['requestor']):
            return '1'

        try:
            user = self.DS.select(User, 'username=' + self.DS.queryFormat(request['requestor']))[0]
        except IndexError:
            return '4'

        try:
            self.MS.data['pushRequests'].append(request['requestor'])
        except KeyError:
            self.MS.data['pushRequests'] = [request['requestor']]

        return '0'

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def recieveGroupMessage(self):
        raise cherrypy.HTTPError(404, 'Not implemented.')

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getStatus(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.RS.checkObjectKeys(self, request, ['profile_username']):
            return '1'

        responseObj = {}

        try:
            if self.MS.data['activeUsers'].count(request['profile_username']) > 0:
                responseObj['status'] = self.MS.data['activeUsers'][profile_username]['status']
            else:
                return '3'
        except KeyError:
            return '3'

        cherrypy.response.headers['Content-Type'] = 'application/json'
        return dumps(responseObj)

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getList(self):
        raise cherrypy.HTTPError(404, 'Not implemented.')

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def report(self):
        raise cherrypy.HTTPError(404, 'Not implemented.')

