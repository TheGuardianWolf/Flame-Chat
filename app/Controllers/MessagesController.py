import cherrypy
from datetime import datetime
from app import Globals
from app.Models.UserModel import User
from json import loads, dumps

class MessagesController(object):
    def __init__(self, services):
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RestfulService']
        self.DS = services['DatabaseService']

    def __isAuthenticated(self):
        if ('authenticated' not in cherrypy.session or cherrypy.session['authenticated'] == False):
            return False
        return True

    @cherrypy.expose
    def get(self, afterTime=None):
        if not self.__isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        #if (datetime.now() - self.lastUserListRefresh).seconds > 10:
        self.__dynamicRefreshActiveUsers()

        userObjs = []

        for user in self.activeUserList:
            userObjs.append(user.serialize())

        json = dumps(userObjs)
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json


