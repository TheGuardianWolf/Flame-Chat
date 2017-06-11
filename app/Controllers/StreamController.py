import cherrypy
from datetime import datetime
from multiprocessing.pool import ThreadPool
from time import sleep
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.UserModel import User
from json import loads, dumps

class StreamController(__Controller):
    def __init__(self, services, controllers):
        super(StreamController, self).__init__(services)

        self.__auth = controllers['AuthController']
        self.__users = controllers['UsersController']
        self.__messages = controllers['MessagesController']
        self.__files = controllers['FilesController']
        self.__profiles = controllers['ProfilesController']
        self.__status = controllers['StatusController']

    def contentPush(self):
        self.__messages.pushMessages()
        self.__files.pushFiles()
        self.MS.data['pushRequests'] = []

    def upkeep(self, sessionData):
        memoryData = self.MS.data

        def pushWorker():
            try:
                if len(memoryData['pushRequests']) > 0:
                    self.contentPush()
            except KeyError:
                memoryData['pushRequests'] = []

        def reportWorker():
            if self.checkTiming(sessionData, 'lastLoginReportTime', 40):
                cherrypy.log.error('Reporting in!')
                self.__auth.dynamicAuth(sessionData['username'], sessionData['passhash'], sessionData=sessionData)
      
        def userListWorker():
            if self.checkTiming(memoryData, 'lastUserListRefresh', 10):
                cherrypy.log.error('Getting user list...')
                self.__users.dynamicRefreshActiveUsers(sessionData['username'], sessionData['passhash'])

        def userInfoWorker():
            if self.checkTiming(memoryData, 'lastUserInfoQuery', 10):
                cherrypy.log.error('Getting user info...')
                self.__users.userInfoQuery(sessionData['username'])

        def pullWorker():
            if self.checkTiming(sessionData, 'lastPulled', 300):
                cherrypy.log.error('Pulling...')
                self.__users.requestRetrieval(sessionData['username'], sessionData=sessionData)

        def userStatusWorker():
            if self.checkTiming(memoryData, 'lastUserStatusQuery', 10):
                cherrypy.log.error('Getting statuses...')
                self.__status.userStatusQuery()
        def userProfileWorker():
            if self.checkTiming(memoryData, 'lastUserProfileQuery', 10):
                cherrypy.log.error('Getting profiles...')
                self.__profiles.userProfileQuery(sessionData['username'])

        def relayMessageWorker():
            if self.checkTiming(memoryData, 'lastRelayMessageSend', 300):
                cherrypy.log.error('Broadcasting messages...')
                self.__messages.relayMessages()

        def relayFileWorker():
            if self.checkTiming(memoryData, 'lastRelayFileSend', 300):
                cherrypy.log.error('Broadcasting files...')
                self.__files.relayFiles()

        def runWorker(worker):
            worker()

        pool = ThreadPool(processes=25)

        asyncWorkers = [
            pullWorker,
            pushWorker,  
            reportWorker,
            userListWorker, 
            userInfoWorker,
            userStatusWorker, 
            userProfileWorker, 
            relayMessageWorker, 
            relayFileWorker
        ]

        workers = [
            
        ]

        for worker in asyncWorkers:
            runWorker(worker)

        #pool.map(runWorker, asyncWorkers)

    @cherrypy.expose
    def index(self):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        cherrypy.response.stream = True
        cherrypy.session['streamEnabled'] = True
        cherrypy.response.headers['Content-Type'] = 'text/event-stream'
        cherrypy.response.headers['Cache-Control'] = 'no-cache'
        errorCode = '-1'
        
        def content():
            while True: 
                try:
                    lastLoginReportTime = cherrypy.session['lastLoginReportTime']
                except KeyError:
                    lastLoginReportTime = None

                sessionData = {
                    'username': cherrypy.session['username'],
                    'passhash': cherrypy.session['passhash'],
                }

                try:
                    sessionData['lastLoginReportTime'] = cherrypy.session['lastLoginReportTime']
                except KeyError:
                    pass

                try:
                    sessionData['authenticated'] = cherrypy.session['authenticated']
                except KeyError:
                    pass

                try:
                    sessionData['lastPulled'] = cherrypy.session['lastPulled']
                except KeyError:
                    pass

                cherrypy.session['streamEnabled'] = True
                cherrypy.session.release_lock()
                self.upkeep(sessionData)

                try:   
                    yield 'ping\n\n'
                except GeneratorExit:
                    self.__auth.dynamicLogoff(sessionData['username'], sessionData['passhash'])
                    try:
                        self.MS.data['userStatus'][sessionData['username']] = 'Offline'
                    except KeyError:
                        pass
                    return                    
                
                sleep(5)
                cherrypy.session.acquire_lock()

                try:
                    cherrypy.session['lastPulled'] = sessionData['lastPulled']
                except KeyError:
                    pass

                try:
                    cherrypy.session['authenticated'] = sessionData['authenticated']
                except KeyError:
                    pass
                
                try:
                    cherrypy.session['lastLoginReportTime'] = sessionData['lastLoginReportTime']
                except KeyError:
                    pass
  
        return content()

    @cherrypy.expose
    def disable(self):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        cherrypy.session['streamEnabled'] = False

        return
