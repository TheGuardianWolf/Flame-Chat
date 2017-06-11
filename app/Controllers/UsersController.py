import cherrypy
from datetime import datetime
from multiprocessing.pool import ThreadPool
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

        for i, results in enumerate(q):
            if len(results) == 0:
                insertions.append(userList[i])
            else:
                for dbEntry in results:
                    if not dbEntry == userList[i]:
                        userList[i].id = dbEntry.id
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
            responseText = response.read()
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
                userList.append(User.deserialize(userObj))

            self.updateTable(userList)
            self.MS.data['activeUsers'] = userList

            return (0, 'Successfully retrieved active user list from login server.')
            
        else:
            return (-2, 'Request error ' + str(status) + ': Login server user list not available.')

    def dynamicRefreshActiveUsers(self, username, passhash):
        self.MS.data['lastUserListRefresh'] = datetime.utcnow()
        
        if self.LS.online:
            (errorCode, errorMessage) = self.__refreshActiveServerUsers(username, passhash)
        else:
            errorCode = -2
            errorMessage = 'Login server is offline.'    
        
        return (errorCode, errorMessage)

    # Call remote peer getList
    def userInfoQuery(self, username):
        self.MS.data['lastUserInfoQuery'] = datetime.utcnow()
        reachableUsers = []
        unreachableUsers = []
        
        potentiallyReachable = []

        if self.LS.online:
            queryList = self.MS.data['activeUsers']
        else:
            queryList = self.DS.select(User)

        # Check reachablity via location filter
        for user in self.MS.data['activeUsers']:
            # Users at this server should marked 'reachable'
            if user.ip == self.LS.ip:
                reachableUsers.append(user)
            else:
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
        pool = ThreadPool(processes=50)
        # Function used for threadpool
        def checkReachable(user):
            return self.RS.get('http://' + str(user.ip) + ':' + str(user.port), '/listAPI', timeout=5)
        responses = pool.map(checkReachable, potentiallyReachable)

        handshakeQueryList = []
        statusQueryList = []
        retrieveMessagesList = []

        # Sort responses
        for i, response in enumerate(responses):
            responseUser = potentiallyReachable[i]
            if response[0] == 200:
                reachableUsers.append(responseUser)
                data = response[1].read().splitlines()
                # Parse api support list
                apiList = data[:-3]
                
                for i, api in enumerate(apiList):
                    try:
                        endpoint = api.split(' ')[0]
                        # People keep not following the specifications on /listAPI
                        if not endpoint == 'Available' or not endpoint == 'Available APIs:':
                            apiList[i] = endpoint
                    except IndexError:
                        continue
                
                apiMeta = UserMeta(None, responseUser.id, 'api', dumps(apiList))
                # Check if entry exists
                q = self.DS.select(UserMeta, 'userId=' + self.DS.queryFormat(responseUser.id) + ' AND key=\'api\'')
                if len(q) > 0:
                    apiMeta.id = q[0].id
                    self.DS.update(apiMeta)
                else:
                    self.DS.insert(apiMeta)

                # Parse standards support list
                try:
                    standardsList = data[-2:]
                    
                    standards = {
                        'encryption': standardsList[0].split(' '),
                        'hashing': standardsList[1].split(' ')
                    }

                    # Again, people not following specifications and including commas where it says to put space...
                    for standard in standards.itervalues():
                        for i in range(0, len(standard)):
                            standard[i].strip(',')

                    standards['encryption'] = sorted(list(set(standards['encryption']) & set(Globals.standards['encryption'])))
                    standards['hashing'] = sorted(list(set(standards['hashing']) & set(Globals.standards['hashing'])))

                    if '0' not in standards['encryption']:
                        standards['encryption'].insert(0, '0')

                    if '0' not in standards['hashing']:
                        standards['hashing'].insert(0, '0')

                except (KeyError, IndexError, ValueError):
                    standards = {
                        'encryption': ['0'],
                        'hashing': ['0']
                    }

                # Test encryption standards higher than 2 based on reciever
                # public key entry
                # Find destination's encryption key and run test
                #if int(standards['encryption'][-1]) > 2:
                #    try:
                #        encryptionKey = responseUser.publicKey
                #        self.SS.encrypt('a', '3', key=encryptionKey)
                #    except (KeyError, ValueError, IndexError):
                #        workingEncryption = []
                #        for i in range(2, -1, -1):
                #            if unicode(i) in standards['encryption']:
                #                workingEncryption.append(unicode(i))
                #        standards['encryption'] = workingEncryption

                standardsMeta = UserMeta(None, responseUser.id, 'standards', dumps(standards))
                # Check if entry exists
                q = self.DS.select(UserMeta, 'userId=' + self.DS.queryFormat(responseUser.id) + ' AND key=\'standards\'')
                if len(q) > 0:
                    standardsMeta.id = q[0].id
                    self.DS.update(standardsMeta)
                else:
                    id = self.DS.insert(standardsMeta)
                    standardsMeta.id = id

                # Make list of users with these optional APIs
                #if '/handshake' in apiList and not (len(standards['encryption']) == 1 and '0' in standards['encryption']):
                #    handshakeQueryList.append((potentiallyReachable[i], standardsMeta))

                if '/getStatus' in apiList:
                    statusQueryList.append(responseUser)

                if '/retrieveMessages' in apiList:
                    retrieveMessagesList.append(responseUser)
            else:
                unreachableUsers.append(responseUser)
        
        self.MS.data['statusQueryList'] = statusQueryList
        self.MS.data['retrieveMessages'] = retrieveMessagesList
        self.MS.data['reachableUsers'] = reachableUsers
        self.MS.data['unreachableUsers'] = unreachableUsers

        # Handshake if available
        pool = ThreadPool(processes=50)
        # Function used for threadpool
        def handshake(params):
            user = params[0]
            standards = loads(params[1].value)
            testStandards = standards['encryption']

            pool = ThreadPool(processes=50)
            def testEncryption(standard):
                if not standard == '0':
                    try:
                        localMessage = 'test'
                        payload = {
                            'message': self.SS.encrypt(localMessage, standard, key=user.publicKey),
                            'sender': 'username',
                            'destination': user.username,
                            'encryption': standard
                        }
                        (status, response) = self.RS.post('http://' + str(user.ip) + ':' + str(user.port), '/handshake', payload, timeout=5)
                        remoteMessage = loads(response.read())['message']
                        if not status == 200 or not remoteMessage.decode('utf-8', 'replace') == localMessage:
                            raise AssertionError('Handshake not successful')
                        else:
                            return True
                    except:
                        return False
                else:
                    return True

            testResults = pool.map(testEncryption, testStandards)
            workingStandards = []
            for i, result in enumerate(testResults):
                if result:
                    working.append(testStandards[i])

            standards['encryption'] = workingStandards
            params[1].value = dumps(standards)
            return params[1]

        standardsMetaList = pool.map(handshake, handshakeQueryList)

        self.DS.updateMany(standardsMetaList)

    def requestRetrieval(self, username):
        try:
            reachableUsers = self.MS.data['reachableUsers']
        except KeyError:
            return

        retrieveFrom = []
        for user in reachableUsers:
            if not user.ip == self.LS.ip:
                retrieveFrom.append(user)

        pool = ThreadPool(processes=50)

        def retrieveMessages(user):
            (status, response) = self.RS.post('http://' + str(user.ip) + ':' + str(user.port), '/retrieveMessages', {'username': username}, timeout=5)

        pool.map(retrieveMessages, retrieveFrom)

        return

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            streamEnabled = cherrypy.session['streamEnabled']
        except KeyError:
            streamEnabled = False

        username = cherrypy.session['username']
        passhash = cherrypy.session['passhash']


        if not streamEnabled:
            pull = False
            if 'pulled' not in cherrypy.session:
                cherrypy.session['pulled'] = True
                pull = True
            cherrypy.session.release_lock()
            if self.checkTiming(self.MS.data, 'lastUserListRefresh', 10):
                self.dynamicRefreshActiveUsers(username, passhash)
            if self.checkTiming(self.MS.data, 'lastUserInfoQuery', 10):
                self.userInfoQuery(username)
            if pull:
                self.requestRetrieval(username)

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

        # Don't include yourself
        filterOut.append(self.DS.queryFormat(username))

        if len(filterOut) > 0:
            unknownUsers = self.DS.select(User, 'username NOT IN ' + self.DS.bracketJoin(',', filterOut))
        else:
            unknownUsers = self.DS.select(User)

        for user in reachableUsers:
            responseObj['reachable'].append(user.serialize())
        for user in unreachableUsers:
            responseObj['unreachable'].append(user.serialize())
        for user in unknownUsers:
            responseObj['unknown'].append(user.serialize())

        return responseObj


