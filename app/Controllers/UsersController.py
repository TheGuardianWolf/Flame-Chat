import cherrypy
from datetime import datetime
from app import Globals
from app.Models.UserModel import User
from json import loads, dumps

class UsersController(__Controller):
    def __init__(self, services):
         super(UsersController, self).__init__(services)
    
    def updateTable(self, userList):
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
                        userList[i].id = dbUser.id
                        updates.append(userList[i])
                        updatesConditions.append('id=' + self.DS.queryFormat(dbUser.id))

        self.DS.insertMany(insertions)
        self.DS.updateMany(updates, updatesConditions)

    def __refreshActivePeerUsers(self):
        raise NotImplementedError('Pure P2P mode not implemented')

    def __refreshActiveServerUsers(self, username, passhash, enc=1):
        payload = {
            'username': username,
            'password': passhash,
            'json': 1
        }

        if enc > 0:
            for key in payload.keys():
                payload[key] = self.SS.serverEncrypt(payload[key])
            payload['enc'] = 1

        (status, response) = self.RS.get(Globals.loginRoot, '/getList', payload)

        if response is not None:
            responseText = response.read();
            try:
                json = loads(responseText)
            except ValueError:
                (errorCode, errorMessage) = responseText.split(',')

                errorCode = int(errorCode)

                if errorCode == 6 and payload['enc'] == 1:
                    (errorCode, errorMessage) = self.__refreshActiveServerUsers(username, passhash, enc=0)
                    errorCode = int(errorCode)

                return (errorCode, errorMessage)

            userList = []

            for userObj in json.values():
                userArgs = []
                userList.append(User.deserialize(userObj))

            self.updateTable(userList)
            self.MS.data['activeUsers'] = userList

            return (0, 'Successfully retrieved active user list from login server.')
            
        else:
            self.MS.data['lastUserListRefresh'] = datetime.now()
            return (-2, 'Request error ' + str(status) + ': Login server user list not available.')

    def dynamicRefreshActiveUsers(self, username, passhash):
        if self.LS.online:
            (errorCode, errorMessage) = self.__refreshActiveServerUsers(username, passhash)
        else:
            errorCode = -2
            errorMessage = 'Login server is offline.'
            
        self.MS.data['lastUserListRefresh'] = datetime.now()
        return (errorCode, errorMessage)

    # Call remote peer getList
    def userInfoQuery(self):
        pass

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
            if self.checkTiming(self.MS.data, 'lastUserListRefresh', 10):
                self.dynamicRefreshActiveUsers(cherrypy.session['username'], cherrypy.session['passhash'])
            if self.checkTiming(self.MS.data, 'lastUserInfoQuery', 10):
                self.userInfoQuery()

        userObjs = []

        try:
            activeUsers = self.MS.data['activeUsers']
        except KeyError:
            activeUsers = []

        for user in activeUsers:
            userObjs.append(user.serialize())

        return userObjs


