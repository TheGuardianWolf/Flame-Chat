import cherrypy
from time import time as getTime
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
from app.Models.UserMetaModel import UserMeta
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
            'Encryption ' + ' '.join(Globals.standards['encryption']),
            'Hashing ' + ' '.join(Globals.standards['hashing'])
        ]

        return '\n'.join(output)

    @cherrypy.expose
    def ping(self, sender):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'
        return '0'

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def recieveMessage(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.checkObjectKeys(request, ['sender', 'destination', 'message', 'stamp']):
            return '1'

        recievedTime = '{0:.3f}'.format(getTime())

        msg = Message.deserialize(request)

        msgId = self.DS.insert(msg)

        msgMetaTime = MessageMeta(None, msgId, 'recievedTime', recievedTime)
        msgMetaStatus = MessageMeta(None, msgId, 'relayAction', 'send')

        self.DS.insertMany([msgMetaTime, msgMetaStatus])

        return '0'
      
    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getPublicKey(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.checkObjectKeys(request, ['sender', 'profile_username']):
            return '1'
        
        try:
            user = self.DS.select(User, 'username=' + self.DS.queryFormat(request['profile_username']))[0]
        except IndexError:
            return '3'

        responseObj = {}

        responseObj['error'] = 0
        responseObj['pubKey'] = user.publicKey

        cherrypy.response.headers['Content-Type'] = 'application/json'
        return dumps(responseObj)

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def handshake(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.checkObjectKeys(request, ['sender', 'destination', 'message', 'encryption']):
            return '1'

        if Globals.standards['encryption'].count(str(request['encryption'])) == 0:
            return '9'

        responseObj = {}

        responseObj['error'] = 0

        try:
            responseObj['message'] = self.SS.decrypt(request['message'], request['encryption'])
        except:
            return '9'

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
        
        # Check requestor standards support list
        conditions = [
            'key=\'standards\'',
            'AND',
            'userId',
            'IN',
            '(SELECT id FROM ' + User.tableName + ' WHERE ip=' + self.DS.queryFormat(cherrypy.request.remote.ip) + ')'
        ]
        
        q = self.DS.select(UserMeta, ' '.join(conditions))

        try:
            if len(q) > 0:
                standards = loads(q[0].value)
                # Assume we already sorted the values in the db on entry
                standard = {
                    'encryption': standards.encryption[-1],
                    'hashing': standards.hashing[-1]
                }
            else:
                raise AssertionError('Support list not found')
        except:
            standard = {
                'encryption': '0',
                'hashing': '0'
            }

        if not standard['encryption'] == '0':
            encProfileObj = {}
            try:
                for key, value in profileObj.items():
                    encProfileObj[key] = self.SS.encrypt(unicode(value), standard['encryption'], key=user.publicKey)
                encProfileObj['encryption'] = standard['encryption']
                profileObj = encProfileObj
            except ValueError:
                pass

        cherrypy.response.headers['Content-Type'] = 'application/json'
        return dumps(profileObj)
    
    @cherrypy.tools.json_in()
    @cherrypy.expose
    def recieveFile(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.checkObjectKeys(request, ['sender', 'destination', 'file', 'filename', 'content_type', 'stamp']):
            return '1'

        recievedTime = '{0:.3f}'.format(getTime())

        f = File.deserialize(request)

        fId = self.DS.insert(f)

        fMetaTime = FileMeta(None, fId, 'recievedTime', recievedTime)
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

        if not self.checkObjectKeys(request, ['requestor']):
            return '1'

        try:
            self.MS.data['pushRequests'].append(request['requestor'])
        except KeyError:
            self.MS.data['pushRequests'] = [request['requestor']]

        return '0'

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getStatus(self):
        if not self.__userFilter(cherrypy.request.remote.ip):
            return '6'

        request = cherrypy.request.json

        if not self.checkObjectKeys(request, ['profile_username']):
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


