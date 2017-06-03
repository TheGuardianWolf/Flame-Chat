import cherrypy
from datetime import datetime
from app import Globals
from app.Models.AuthModel import Auth
from app.Models.MessageModel import Message
from app.Models.UserModel import User

class PublicController(object):
    def __init__(self, services):
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RestfulService']
        self.DS = services['DatabaseService']

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPError(403, 'You don\'t have permission to access / on this server.')
    
    @cherrypy.expose
    def listAPI(self):
        pass

    @cherrypy.expose
    def ping(self, sender):
        pass

    @cherrypy.tools.json_in()
    @cherrypy.expose
    def recieveMessage(self):
        pass

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

