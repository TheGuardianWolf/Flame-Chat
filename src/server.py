import cherrypy
import globals


class Server(object):
    def __init__(self):
        self.mapper = cherrypy.dispatch.MethodDispatcher()

        self.appConfig = {
            "/": {
                "request.dispatch": self.mapper,
                "tools.sessions.on": True,
                "tools.staticdir.on": True,
                "tools.staticdir.dir": globals.webRoot,
                "tools.staticdir.index": "index.html"
            }
        }

    def route(self):
        cherrypy.tree.mount(None, "/", config=self.appConfig)

    # a blocking call that starts the web application listening for requests
    def start(self, port=8080):
        self.route()
        cherrypy.config.update({"server.socket_host": "0.0.0.0", })
        cherrypy.config.update({"server.socket_port": port, })
        cherrypy.engine.signals.subscribe()
        cherrypy.engine.start()
        cherrypy.engine.block()

    # stops the web application
    def stop(self):
        cherrypy.engine.stop()


def main():
    # my code here
    server = Server()
    server.start()


if __name__ == "__main__":
    main()
