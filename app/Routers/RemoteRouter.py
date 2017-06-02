import cherrypy
from app import Globals

class RemoteRouter(object):
    def __init__(self, services):
        self.services = services

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPError(403, 'You don\'t have permission to access / on this server.')