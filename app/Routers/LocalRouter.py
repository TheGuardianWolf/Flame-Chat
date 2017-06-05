import cherrypy
from app import Globals
from app.Controllers.AuthController import AuthController
from app.Controllers.UsersController import UsersController
from app.Controllers.MessagesController import MessagesController

class LocalRouter(object):
    def __init__(self, services):
        self.services = services
        self.auth = AuthController(services)
        self.users = UsersController(services)
        self.messages = MessagesController(services)