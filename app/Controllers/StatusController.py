import cherrypy
from datetime import datetime
from multiprocessing.pool import ThreadPool
from app import Globals
from app.Controllers.__Controller import __Controller
from json import loads, dumps

class StatusController(__Controller):
    def __init__(self, services):
         super(ProfilesController, self).__init__(services)

    # Call remote peer getStatus
    def userStatusQuery(self):
        try:
            statusQueryList = self.MS.data['statusQueryList']
        except KeyError:
            statusQueryList = []

        pool = ThreadPool(processes=50)
        def checkStatus(user):
            payload = {
                'profile_username': user.username
            }
            (status, response) = self.RS.post('http://' + str(user.ip), '/getStatus', payload)
            if status == 200:
                return (user, loads(response.read())['status'])
            else:
                return (user, 'offline')
        responses = pool.map(checkStatus, statusQueryList)

        for user, status in responses:
            try:
                self.MS.data['userStatus'][user.username] = status
            except KeyError:
                self.MS.data['userStatus'] = {}
                self.MS.data['userStatus'][user.username] = status


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            streamEnabled = cherrypy.session['streamEnabled']
        except KeyError:
            streamEnabled = False

        if not streamEnabled:
            cherrypy.session.release_lock()
            if self.checkTiming(self.MS.data, 'lastUserStatusQuery', 10):
                self.userStatusQuery()

        try:
            responseObj = self.MS.data['userStatus']
        except KeyError:
            return {}

        return responseObj

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def post(self):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            request = cherrypy.request.json
        except AttributeError:
            raise cherrypy.HTTPError(400, 'JSON payload not sent.')

        if not self.checkObjectKeys(request, ['status']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')

        try:
            self.MS.data['userStatus'][cherrypy.session['username']] = request['status']
        except KeyError:
            self.MS.data['userStatus'] = {}

        return
