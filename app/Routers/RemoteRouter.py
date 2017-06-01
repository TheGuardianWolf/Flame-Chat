import cherrypy
import Globals

class RemoteRouter(object):
    #_cp_config = {
    #    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    #    'tools.sessions.on': True
    #}

    def __init__(self, services):
        self.services = services