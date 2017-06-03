import cherrypy
from datetime import datetime
from json import loads, dumps
from os import path
from app import Globals
from app.Models.AuthModel import Auth
from app.Models.MessageModel import Message
from app.Models.UserModel import User

class PublicController(object):
    _cp_config = {
        'tools.sessions.on': False
    }

    encoding = ['0', '2']
    encryption = ['0', '2', '3', '4']
    hashing = ['0', '1', '2', '3', '4']

    def __init__(self, services):
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RestfulService']
        self.DS = services['DatabaseService']

        f = open(path.join(Globals.appRoot, 'publicAPI.json'))
        self.apiList = loads(f.read())
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
        request['encoding'] = int(encoding)
        msg = Message.deserialize(request)
        self.DS.insert(msg)
        
    @cherrypy.tools.json_in()
    @cherrypy.expose
    def acknowledge(self):
        pass

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getPublicKey(self):
        pass

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def handshake(self):
        pass

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getProfile(self):
        pass

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def retrieveMessages(self):
        pass

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def recieveGroupMessage(self):
        pass

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getStatus(self):
        pass

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getList(self):
        pass

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def report(self):
        pass

