import cherrypy
from app import Globals
from app.Controllers.PublicController import PublicController

# Simple hack to have a placeholder router for public api routes
def RemoteRouter(services):
    """
    Routes remote requests to the PublicController
    """
    return PublicController(services)

#class RemoteRouter(object):
#    def __init__(self, services):
#        self.services = services

#    @cherrypy.expose
#    def index(self):
#        raise cherrypy.HTTPError(403, 'You don\'t have permission to access / on this server.')