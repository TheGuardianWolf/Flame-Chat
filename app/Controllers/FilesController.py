import cherrypy
from datetime import datetime
from app import Globals
from app.Controllers import __Controller
from app.Models.FileModel import File
from json import loads, dumps

class FilesController(__Controller):
    def __init__(self, services):
        super(FilesController, self).__init__(services)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self, since=None):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        self.__dynamicRefreshActiveUsers()

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

        if not self.RS.checkObjectKeys(request, ['destination', 'file', 'filename', 'mimetype']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')