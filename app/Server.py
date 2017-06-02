import cherrypy
from app import Globals
from app.Services.DatabaseService import DatabaseService
from app.Services.LoginService import LoginService
from app.Services.SecureService import SecureService
from app.Services.RestfulService import RestfulService
from app.Routers.LocalRouter import LocalRouter
from app.Routers.RemoteRouter import RemoteRouter

class Server(object):
    def __init__(self):
        self.globalConfig = {
            'server.socket_host': '0.0.0.0', 
            'server.socket_port': Globals.publicPort,
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.encode.encoding': 'utf-8'
        }

        self.staticConfig = {
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': Globals.webRoot,
                'tools.staticdir.index': 'index.html'
            },
        }

        self.services = {
            'DatabaseService': DatabaseService(Globals.dbPath),
            'LoginService': LoginService(),
            'SecureService': SecureService(),
            'RestfulService': RestfulService()
        }

        self.routers = {
            'LocalRouter': LocalRouter(self.services),
            'RemoteRouter': RemoteRouter(self.services)
        }

    def mountTree(self):
        cherrypy.tree.mount(self.routers['RemoteRouter'], '/', config=self.staticConfig)
        cherrypy.tree.mount(self.routers['LocalRouter'], '/local')

    # a blocking call that starts the web application listening for requests
    def start(self):
        self.mountTree()
        cherrypy.config.update(self.globalConfig)
        if hasattr(cherrypy.engine, 'signal_handler'):
            cherrypy.engine.signal_handler.subscribe()
        if hasattr(cherrypy.engine, 'console_control_handler'):
            cherrypy.engine.console_control_handler.subscribe()
        cherrypy.engine.start()
        cherrypy.engine.block()

    # stops the web application
    def stop(self):
        cherrypy.engine.stop()


def main():
    server = Server()
    server.start()


if __name__ == '__main__':
    main()
