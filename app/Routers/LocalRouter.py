import cherrypy
import Globals
from app.Controllers.AuthController import AuthController

class LocalRouter(object):

    def __init__(self, services):
        self.services = services
        self.auth = AuthController(services)

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')