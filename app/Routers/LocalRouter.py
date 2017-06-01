import cherrypy
import Globals
from app.Controllers.AuthController import AuthController

class LocalRouter(object):
    #_cp_config = {
    #    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    #    'tools.sessions.on': True
    #}

    def __init__(self, services):
        self.services = services
        self.auth = AuthController(services)

    @cherrypy.expose
    def index(self):
        #return 'Reached LocalRouter'
        raise cherrypy.HTTPError(403, r"You don't have permission to access / on this server.")