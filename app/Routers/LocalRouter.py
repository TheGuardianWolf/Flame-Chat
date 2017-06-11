import cherrypy
from app import Globals
from app.Controllers.AuthController import AuthController
from app.Controllers.UsersController import UsersController
from app.Controllers.MessagesController import MessagesController
from app.Controllers.FilesController import FilesController
from app.Controllers.ProfilesController import ProfilesController
from app.Controllers.StatusController import StatusController
from app.Controllers.StreamController import StreamController

class LocalRouter(object):
    """
    Routes requests to local API.
    """
    def __init__(self, services):
        self.auth = AuthController(services)
        self.users = UsersController(services)
        self.messages = MessagesController(services)
        self.files = FilesController(services)
        self.profiles = ProfilesController(services)
        self.status = StatusController(services)

        controllers = {
            'AuthController': self.auth,
            'UsersController': self.users,
            'MessagesController': self.messages,
            'FilesController': self.files,
            'ProfilesController': self.profiles,
            'StatusController': self.status
        }

        self.stream = StreamController(services, controllers)
