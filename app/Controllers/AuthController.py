import cherrypy

import Globals

class AuthController(object):
    def __init__(self, services):
        self.services = services
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RestfulService']

    def __loginServerAuth(self, username, passhash):
        payload = {
            'username': username,
            'password': passhash,
            'location': self.LS.findLocation(),
            'ip': self.LS.getIP(),
            'port': Globals.publicPort,
            'pubkey': self.SS.publicKey.exportKey('PEM')
        }

        for key in payload.keys():
            payload[key] = self.SS.serverEncrypt(str(payload[key]))

        payload['enc'] = 1

        return self.RS.get(Globals.loginRoot, '/report', payload)

    @cherrypy.expose
    def index(self):
        return self.post().read()

    @cherrypy.expose
    def get(self):
        cherrypy.response.headers["Content-Type"] = "text/event-stream;charset=utf-8"
        return "event: time\n" + "data: " + str(time.time()) + "\n\n";

    @cherrypy.expose
    def post(self, username='jfan082', passhash=self.LS.getPassword()):
        return self.__loginServerAuth(username, passhash)