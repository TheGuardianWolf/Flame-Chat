import cherrypy
from datetime import datetime
from json import loads, dumps
from binascii import hexlify
from os import path
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.AuthModel import Auth
from app.Models.MessageModel import Message
from app.Models.MessageMetaModel import MessageMeta
from app.Models.UserModel import User
from app.Models.ProfileModel import Profile
from app.Models.FileModel import File
from app.Models.FileMetaModel import FileMeta

class PublicController(__Controller):
    _cp_config = {
        'tools.sessions.on': False
    }

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
            #'Encoding ' + ' '.join(Globals.standards.encoding),
            'Encryption ' + ' '.join(Globals.standards.encryption),
            'Hashing ' + ' '.join(Globals.standards.hashing)
        ]

        return '\n'.join(output)

    @cherrypy.expose
    def ping(self, sender):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'
        return '0'

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def recieveMessage(self):#, encoding='0'):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.checkObjectKeys(self, request, ['sender', 'destination', 'message', 'stamp']):
            return '1'

        #request['encoding'] = unicode(encoding)

        recievedTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

        msg = Message.deserialize(request)

        msgId = self.DS.insert(msg)

        msgMetaTime = MessageMeta(None, msgId, 'recievedTime', recievedTime)
        msgMetaStatus = MessageMeta(None, msgId, 'relayAction', 'unsent')

        self.DS.insertMany(msgMetaTime + msgMetaStatus)

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

        if not self.checkObjectKeys(self, request, ['sender', 'profile_username']):
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

        if not self.checkObjectKeys(self, request, ['sender', 'destination', 'message', 'encryption']):
            return '1'

        if Globals.standards.encryption.count(str(request['encryption'])) == 0:
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
        #profileObj['encoding'] = 0

        cherrypy.response.headers['Content-Type'] = 'application/json'
         
        if user.publicKey is not None:
            encProfileObj = {}
            try:
                for key, value in profileObj.items():
                    encProfileObj[key] = self.SS.encrypt(unicode(value), '3', key=user.publicKey)
                encProfileObj['encryption'] = 3
                return dumps(profileObj)
            except ValueError:
                pass

        return dumps(profileObj)
    
    @cherrypy.tools.json_in()
    @cherrypy.expose
    def recieveFile(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.checkObjectKeys(self, request, ['sender', 'destination', 'file', 'filename', 'content_type', 'stamp', 'hashing']):
            return '1'

        f = File.deserialize(request)

        fId = self.DS.insert(f)

        fMetaTime = FileMeta(None, fID, 'recievedTime', recievedTime)
        fMetaStatus = FileMeta(None, fId, 'relayAction', 'unsent')

        self.DS.insertMany(fMetaTime + fMetaStatus)

        return '0'

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def retrieveMessages(self):
        raise cherrypy.HTTPError(404, 'Not implemented.')

        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.checkObjectKeys(self, request, ['requestor']):
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

        if not self.checkObjectKeys(self, request, ['profile_username']):
            return '1'

        responseObj = {}

        try:
            if request['profile_username'] in self.MS.data['userStatus']:
                responseObj['status'] = self.MS.data['userStatus'][request['profile_username']]
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

