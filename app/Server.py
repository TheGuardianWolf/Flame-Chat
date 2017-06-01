import cherrypy
import Globals
from app.Services.DatabaseService import DatabaseService
from app.Services.LoginService import LoginService
from app.Services.SecureService import SecureService

class Server(object):
    def __init__(self):
        self.mapper = cherrypy.dispatch.MethodDispatcher()
        
        self.appConfig = {
            '/': {
                'request.dispatch': self.mapper,
                'tools.sessions.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': Globals.webRoot,
                'tools.staticdir.index': 'index.html'
            }
        }

        self.services = {
            'DatabaseService': DatabaseService(),
            'LoginService': LoginService(),
            'SecureService': SecureService()
        }

        self.controllers = {
        }

    def mountTree(self):
        cherrypy.tree.mount(None, '/', config=self.appConfig)

    # a blocking call that starts the web application listening for requests
    def start(self, port=8080):
        self.mountTree()
        cherrypy.config.update({
            'server.socket_host': '0.0.0.0', 
            'server.socket_port': port
        })
        cherrypy.engine.signals.subscribe()
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
