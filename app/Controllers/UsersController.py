import cherrypy
from datetime import datetime
from multiprocessing.pool import ThreadPool
import re
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.UserModel import User
from app.Models.UserMetaModel import UserMeta
from binascii import unhexlify
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
        updateUserId = []
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

        idList = self.DS.insertMany(insertions)
        self.DS.updateMany(updates)

        for i, id in enumerate(idList):
            insertions[i].id = id

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
            self.MS.data['lastUserListRefresh'] = datetime.utcnow()
            return (-2, 'Request error ' + str(status) + ': Login server user list not available.')

    def dynamicRefreshActiveUsers(self, username, passhash):
        if self.LS.online:
            (errorCode, errorMessage) = self.__refreshActiveServerUsers(username, passhash)
        else:
            errorCode = -2
            errorMessage = 'Login server is offline.'
            
        self.MS.data['lastUserListRefresh'] = datetime.utcnow()
        return (errorCode, errorMessage)

    # Call remote peer getList
    def userInfoQuery(self, username):
        reachableUsers = []
        unreachableUsers = []
        
        potentiallyReachable = []

        # Check reachablity via location filter
        for user in self.MS.data['activeUsers']:
            try:
                try:
                    remoteLocation = int(user.location)
                except TypeError:
                    raise AssertionError('User location unparsable')
                if not remoteLocation == self.LS.location and not remoteLocation == 2:
                    raise AssertionError('User in unaccessable location')
                potentiallyReachable.append(user)
            except AssertionError:
                unreachableUsers.append(user)
                continue

        # Check reachablity via request
        pool = ThreadPool(processes=10)
        # Function used for threadpool
        def checkReachable(user):
            return self.RS.get('http://' + str(user.ip), '/listAPI', timeout=1)
        responses = pool.map(checkReachable, potentiallyReachable)

        # Sort responses
        handshakeList = []
        for i, response in enumerate(responses):
            if response[0] == 200:
                reachableUsers.append(potentiallyReachable[i])
                data = response[1].read().splitlines()
                # Parse api support list
                apiList = data[:-3]
                for i, api in enumerate(apiList):
                    try:
                        apiList[i] = api.split(' ')[0]
                    except IndexError:
                        continue
                
                apiMeta = UserMeta(None, potentiallyReachable[i].id, 'api', dumps(apiList))
                # Check if entry exists
                q = self.DS.select(UserMeta, 'userId=' + self.DS.queryFormat(potentiallyReachable[i].id) + ' AND key=\'api\'')
                if len(q) > 0:
                    apiMeta.id = q[0].id
                    self.DS.update(apiMeta)
                else:
                    self.DS.insert(apiMeta)

                # Parse standards support list
                standardsList = data[-3:]
                try:
                    standards = {
                        'encoding': sorted(list(set(standardsList[0]) & set(Globals.standards['encoding']))),
                        'encryption': sorted(list(set(standardsList[1]) & set(Globals.standards['encryption']))),
                        'hashing': sorted(list(set(standardsList[2]) & set(Globals.standards['hashing'])))
                    }
                except:
                    standards = {
                        'encoding': ['0'],
                        'encryption': ['0'],
                        'hashing': ['0']
                    }

                standardsMeta = UserMeta(None, potentiallyReachable[i].id, 'standards', dumps(standards))
                # Check if entry exists
                q = self.DS.select(UserMeta, 'userId=' + self.DS.queryFormat(potentiallyReachable[i].id) + ' AND key=\'standards\'')
                if len(q) > 0:
                    standardsMeta.id = q[0].id
                    self.DS.update(standardsMeta)
                else:
                    id = self.DS.insert(standardsMeta)
                    standardsMeta.id = id

                if '/handshake' in apiList and not (len(standards['encryption']) == 1 and '0' in standards['encryption']):
                    handshakeList.append((potentiallyReachable[i], standardsMeta))
        
        self.MS.data['reachableUsers'] = reachableUsers
        self.MS.data['unreachableUsers'] = unreachableUsers

        # Handshake if available
        pool = ThreadPool(processes=10)
        # Function used for threadpool
        def handshake(params):
            user = params[0]
            standards = loads(params[1].value)
            testStandards = standards['encryption']

            notWorking = []
            for i in range(0, len(testStandards)):
                if not testStandards[i] == '0':
                    try:
                        localMessage = 'test'
                        payload = {
                            'message': self.SS.encrypt(localMessage, testStandards[i], key=unhexlify(user.publicKey)),
                            'sender': 'username',
                            'destination': user.username,
                            'encryption': testStandards[i]
                        }
                        (status, response) = self.RS.post('http://' + str(user.ip), '/handshake', payload, timeout=1)
                        remoteMessage = loads(response.read())['message']
                        if not status == 200 or not remoteMessage.decode('utf-8', 'replace') == localMessage:
                            raise AssertionError('Handshake not successful')
                    except:
                        notWorking.append(testStandards[i])
            standards['encryption'] = sorted(list(set(testStandards).difference(notWorking)))
            params[1].value = dumps(standards)
            return params[1]

        standardsMetaList = pool.map(handshake, handshakeList)

        self.DS.updateMany(standardsMetaList)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            streamEnabled = cherrypy.session['streamEnabled']
        except KeyError:
            streamEnabled = False

        username = cherrypy.session['username']
        passhash = cherrypy.session['passhash']

        if not streamEnabled:
            cherrypy.session.release_lock()
            if self.checkTiming(self.MS.data, 'lastUserListRefresh', 10):
                self.dynamicRefreshActiveUsers(username, passhash)
            if self.checkTiming(self.MS.data, 'lastUserInfoQuery', 10):
                self.userInfoQuery(username)

        responseObj = {
            'reachable': [],
            'unreachable': [],
            'unknown': []
        }

        filterOut = []

        try:
            reachableUsers = self.MS.data['reachableUsers']
        except KeyError:
            reachableUsers = []

        try:
            unreachableUsers = self.MS.data['unreachableUsers']
        except KeyError:
            unreachableUsers = []

        for user in reachableUsers + unreachableUsers:
            filterOut.append(self.DS.queryFormat(user.username))

        if len(filterOut) > 0:
            unknownUsers = self.DS.select(User, 'username NOT IN ' + self.DS.bracketJoin(',', filterOut))
        else:
            unknownUsers = self.DS.select(User)

        for user in reachableUsers:
            responseObj['reachable'].append(user.deserialize())
        for user in unreachableUsers:
            responseObj['unreachable'].append(user.deserialize())
        for user in unknownUsers:
            responseObj['unknown'].append(user.deserialize())

        return responseObj


