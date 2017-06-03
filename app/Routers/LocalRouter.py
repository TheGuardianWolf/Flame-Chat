import cherrypy
from app import Globals
from app.Controllers.AuthController import AuthController
from app.Controllers.UsersController import UsersController

class LocalRouter(object):

    def __init__(self, services):
        self.services = services
        self.auth = AuthController(services)
        self.users = UsersController(services)