import cherrypy
from datetime import datetime
from app import Globals
from app.Controllers.__Controller import __Controller
from json import loads, dumps

class StatusController(__Controller):
    def __init__(self, services):
         super(ProfilesController, self).__init__(services)

    # Call remote peer getStatus
    def userStatusQuery(self):
        pass

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def post(self):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            request = cherrypy.request.json
        except AttributeError:
            raise cherrypy.HTTPError(400, 'JSON payload not sent.')

        if not self.checkObjectKeys(request, ['status']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')
