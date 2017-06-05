import cherrypy
from datetime import datetime
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.UserModel import User
from json import loads, dumps

class MessagesController(__Controller):
    def __init__(self, services):
        super(MessagesController, self).__init__(services)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self, since=None):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        userObjs = []

        for user in self.activeUserList:
            userObjs.append(user.serialize())

        json = dumps(userObjs)
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def post(self):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            request = cherrypy.request.json
        except AttributeError:
            raise cherrypy.HTTPError(400, 'JSON payload not sent.')

        if not self.checkObjectKeys(request, ['destination', 'message']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')