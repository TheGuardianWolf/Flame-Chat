import cherrypy
from datetime import datetime
from app import Globals
from app.Models.UserModel import User
from json import loads, dumps

class UsersController(object):
    def __init__(self, services):
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RestfulService']
        self.DS = services['DatabaseService']

    def __isAuthenticated(self):
        if ('authenticated' not in cherrypy.session or cherrypy.session['authenticated'] == False):
            return False
        return True
    
    def __updateUsersTable(self, userList):
        conditionList = []
        for user in userList:
            conditionList.append('username=' + self.DS.queryFormat(user.username))
        modelsList = [User] * len(conditionList)
        q = self.DS.selectMany(modelsList, conditionList)

        insertions = []
        updates = []
        updatesConditions = []

        for i, results in enumerate(q):
            if len(results) == 0:
                insertions.append(userList[i])
            else:
                for dbUser in results:
                    if not dbUser == userList[i]:
                        updates.append(userList[i])
                        updatesConditions.append('id=' + self.DS.queryFormat(dbUser.id))

        self.DS.insertMany(insertions)
        self.DS.updateMany(updates, updatesConditions)

    def __refreshActivePeerUsers(self):
        pass

    def __refreshActiveServerUsers(self, enc=1):
        if not self.__isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        payload = {
            'username': cherrypy.session['username'],
            'password': cherrypy.session['passhash'],
            'json': 1
        }

        if enc > 0:
            for key in payload.keys():
                payload[key] = self.SS.serverEncrypt(str(payload[key]))
            payload['enc'] = 1

        (status, response) = self.RS.get(Globals.loginRoot, '/getList', payload)

        if response is not None:
            responseText = response.read();
            try:
                json = loads(responseText)
            except ValueError:
                (errorCode, errorText) = responseText.split(',')

                errorCode = int(errorCode)

                if errorCode == 6 and payload['enc'] == 1:
                    (errorCode, errorMessage) = self.__refreshActiveServerUsers(enc=0)
                    errorCode = int(errorCode)

                return (errorCode, errorMessage)

            userList = []

            for userObj in json.values():
                userArgs = []
                for entryName, entryType in User.tableSchema:
                    try:
                        if entryType.find('integer') > -1:
                            arg = int(userObj[entryName])
                        else:
                            arg = str(userObj[entryName])
                    except KeyError:
                        arg = None
                    userArgs.append(arg)
                userList.append(User(*userArgs))

            self.__updateUsersTable(usersList)
            self.activeUserList = usersList
            return (0, 'Successfully retrieved active user list from login server.')
            
        else:
            self.lastUserListRefresh = datetime.now()
            return (-2, 'Request error ' + str(status) + ': Login server user list not available.')

    def __dynamicRefreshActiveUsers(self):
        if self.LS.online:
            (errorCode, errorMessage) = self.__refreshActiveServerUsers()
            if errorCode == -2:
                (errorCode, errorMessage) = self.__refreshActivePeerUsers()
                errorMessage += ' Request to login server failed with unhandled error.'
        else:
            (errorCode, errorMessage) = self.__refreshActivePeerUsers()
            errorMessage += ' Login server offline or unreachable.'
            
        self.lastUserListRefresh = datetime.now()
        return (errorCode, errorMessage)

    #@cherrypy.expose
    #def stream(self):
    #    if not self.__isAuthenticated():
    #        raise cherrypy.HTTPError(403, 'User not authenticated')

    #    cherrypy.response.headers['Content-Type'] = 'text/event-stream;charset=utf-8'

    #    if (datetime.now() - self.lastUserListRefresh.seconds) > 10:
    #        lastActiveUsers = self.activeUserList
    #        (errorCode, errorMessage) = self.__dynamicRefreshActiveUsers()

    #    return '\n\n'

    @cherrypy.expose
    def getActiveUsers(self):
        if not self.__isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        if (datetime.now() - self.lastUserListRefresh.seconds) > 10:
            self.__dynamicRefreshActiveUsers()

        userObjs = []

        for user in self.activeUserList:
            userObjs.append(user.serialize())

        json = dumps(userObjs)
        cherrypy.response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return json


