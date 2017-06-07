import cherrypy
from datetime import datetime
from multiprocessing.pool import ThreadPool
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.MessageModel import Message
from app.Models.MessageMetaModel import MessageMeta
from app.Models.UserModel import User
from app.Models.UserMetaModel import UserMeta
from json import loads, dumps

class MessagesController(__Controller):
    def __init__(self, services):
        super(MessagesController, self).__init__(services)
        self.noEncrypt = ['sender', 'destination', 'encryption']

    def decodeMessage(self, msg, encoding):
        if str(encoding) == '0':
            return unicode(msg)
        elif str(encoding) == '2':
            return unicode(msg.decode('utf-8', 'replace'))
        else:
            raise ValueError('Unrecognised encoding standard')

    def encodeMessage(self, msg, encoding):
        if str(encoding) == '0':
            return unicode(msg.encode('ascii', 'replace'))
        elif str(encoding) == '2':
            return unicode(msg.encode('utf-8', 'replace'))
        else:
            raise ValueError('Unrecognised encoding standard')

    def duplicateCheck(self, a, b):
        # Check if b is a duplicate of a
        if a.hashing is not None and b.hashing is not None and a.hashing == b.hashing:
            try:
                aU = self.SS.cmpHash(''.join([u'>', unicode(a.hash), unicode(a.stamp), u'<']))
                bU = self.SS.cmpHash(''.join([u'>', unicode(b.hash), unicode(b.stamp), u'<']))
                if aU == bU:
                    return True
                else:
                    return False
            except (ValueError, TypeError):
                try:
                    aU = self.SS.cmpHash(''.join([u'>', unicode(a.message), unicode(a.stamp), u'<']))
                    bU = self.SS.cmpHash(''.join([u'>', unicode(b.message), unicode(b.stamp), u'<']))
                    if aU == bU:
                        return True
                    else:
                        return False
                except (ValueError, TypeError):
                    return False
     
    def upsertMessageMeta(self, metaKey, metaValue, messageList):
        insertList = []
        updateList = []
        for msg in messageList:
            q = self.DS.select(MessageMeta, 'messageId=' + self.DS.queryFormat(msg.id) + ' AND key=\'' + metaKey + '\'')
            if len(q) > 0:
                updateList.append(MessageMeta(q[0].id, msg.id, metaKey, metaValue))
            else:
                insertList.append(MessageMeta(None, msg.id, metaKey, metaValue))
        if len(updateList) > 0:
            self.DS.updateMany(updateList)
        if len(insertList) > 0:
            self.DS.insertMany(insertList)

    def deleteMessages(self, messageList):
        modelsList = []
        conditionsList = []
        for msg in messageList:
            modelsList.append(Message)
            conditionsList.append('id=' + self.DS.queryFormat(msg.id))
            modelsList.append(MessageMeta)
            conditionsList.append('messageId=' + self.DS.queryFormat(msg.id))
        self.DS.deleteMany(modelsList, conditionsList)

    def pushMessages(self):
        pushList = []
        for username in self.MS.data['pushRequests']:
            conditions = [
                'destination=' + self.DS.queryFormat(username),
                'AND'
                'id',
                'IN',
                '(SELECT messageId FROM ' + MessageMeta.tableName + ' WHERE key=\'relayAction\' AND (value=\'send\' OR value=\'broadcast\'))'
            ]
            toSend = self.DS.select(Message, ' '.join(conditions))
            pushList.append(toSend)

        # Helper function to push to individual users
        def push(messageList):
            # Cherrypy servers limited to 10 concurrent requests per second
            pool = ThreadPool(processes=5)
            pool.map(self.sendMessage, messageList)

        pool = ThreadPool(processes=50)
        pool.map(push, pushList)

    def relayMessages(self):
        self.MS.data['lastRelayMessageSend'] = datetime.utcnow()
        conditions = [
            'id',
            'IN',
            '(SELECT messageId FROM ' + MessageMeta.tableName + ' WHERE key=\'relayAction\' AND value=\'send\')'
        ]
        toSend = self.DS.select(Message, ' '.join(conditions))
        conditions = [
            'id',
            'IN',
            '(SELECT messageId FROM ' + MessageMeta.tableName + ' WHERE key=\'relayAction\' AND value=\'broadcast\')'
        ]
        toBroadcast = self.DS.select(Message, ' '.join(conditions))

        pool = ThreadPool(processes=5)
        pool.map(self.sendMessage, toSend)
        pool.map(self.broadcastMessage, toBroadcast)

    def sendMessage(self, message, relayTo=None):
        destination = relayTo

        if relayTo is None:
            # Find user entry
            for user in reachableUsers:
                if message.destination == user.username:
                    destination = user

        if destination is not None:
            if not destination.ip == self.LS.ip:
                # Send the message if destination is not local
                (status, response) = self.RS.post('http://' + str(destination.ip), '/receiveMessage', payload)
            # Mark message action as store if direct send, else as send if relayed
            if relayTo is None:
                self.upsertMessageMeta('relayAction', 'store', [message])
            else:
                # Should I still attempt direct send after relaying?
                # Currently, yes, as it's best not to rely on other relay nodes
                self.upsertMessageMeta('relayAction', 'send', [message])
        return
                

    def broadcastMessage(self, message):
        try:
            reachableUsers = self.MS.data['reachableUsers']
        except KeyError:
            reachableUsers = []
        
        reachableRemoteUsers = []
        
        # Filter out the local users from the broadcast list
        # Messages with local user as destination and broadcast will be held indefinately
        for user in reachableUsers:
            if user.ip == self.LS.ip:
                if user.username == message.destination:
                    return
            else:
                reachableRemoteUsers.append(user)
    
        # Check if destination is on the broadcast list, and if so, change to direct send
        for user in reachableRemoteUsers:
            if message.destination == user.username:
                # Change to direct send
                return self.sendMessage(message)
                
        paramList = []
        for user in reachableRemoteUsers:
            paramList.append((user, message))
        pool = ThreadPool(processes=25)
        # Can only use one argument with map, so use helper function to seperate parameters from a tuple
        def delegate(params):
            self.sendMessage(params[0], relayTo=params[1])
        pool.map(delegate, paramList)
            

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self, target, since=None):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            streamEnabled = cherrypy.session['streamEnabled']
        except KeyError:
            streamEnabled = False

        username = cherrypy.session['username']

        cherrypy.session.release_lock()
        if not streamEnabled:
            if self.checkTiming(self.MS.data, 'lastRelayMessageSend', 300):
                self.relayMessages()

        if since is None:
            conditions = [
                '(sender=' + self.DS.queryFormat(username),
                'AND'
                'destination=' + self.DS.queryFormat(target) + ')',
                'OR',
                '(sender=' + self.DS.queryFormat(target),
                'AND'
                'destination=' + self.DS.queryFormat(username) + ')'
            ]
            q = self.DS.select(Message, ' '.join(conditions))
        else:
            try:
                timeString = datetime.strptime(since.split('.')[0], "%Y-%m-%dT%H:%M:%SZ" )
            except (ValueError, IndexError) as e:
                raise cherrypy.HTTPError(400, 'Malformed time.')
            conditions = [
                '(sender=' + self.DS.queryFormat(username),
                'AND'
                'destination=' + self.DS.queryFormat(target) + ')',
                'OR',
                '(sender=' + self.DS.queryFormat(target),
                'AND'
                'destination=' + self.DS.queryFormat(username) + ')',
                'AND'
                'id',
                'IN',
                '(SELECT messageId FROM ' + MessageMeta.tableName + ' WHERE key=\'recievedTime\' AND value > \'' + timeString + '\')'
            ]
            q = self.DS.select(Message, ' '.join(conditions))

        returnObj = []

        removeQueue = []
        markReadQueue = []

        for i in range(0, len(q)):
            inbound = q[i].destination == username
            try:
                # Decrypt if encrypted
                if int(q[i].encryption) > 0:
                    for entryName, entryType in q[i].tableSchema:
                        if entryName not in self.noEncrypt:
                            self.SS.decrypt(getattr(q[i], entryName), q[i].encryption)

                # Run checks on inbound messages
                if inbound:
                    # Check hashes of inbound
                    if int(q[i].hashing) > 0:
                        if not self.SS.hash(q[i].message, q[i].hashing, sender=q[i].sender) == q[i].hash:
                            raise ValueError('Hashes do not match')

                    # Check for inbound duplicates
                    for msg in markReadQueue:
                        if self.duplicateCheck(msg, q[i]):
                            raise ValueError('Duplicate message')

                    # Mark sent if inbound and unmarked
                    if (q[i].destination == username):
                        markReadQueue.append(q[i])

                # Store object to be returned
                returnObj.append(q[i].serialize()) 
            except ValueError:
                removeQueue.append(q[i])
                continue

            # Process mark-reads
            self.upsertMessageMeta('relayAction', 'store', markReadQueue)
            
            # Process removals
            self.deleteMessages(removeQueue)

        return returnObj


    @cherrypy.expose
    @cherrypy.tools.json_in()
    def post(self):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            request = cherrypy.request.json
        except AttributeError:
            raise cherrypy.HTTPError(400, 'JSON payload not sent.')

        if not self.checkObjectKeys(request, ['destination', 'message', 'stamp']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')

        username = cherrypy.session['username']
        cherrypy.session.release_lock()

        currentTime = datetime.utcnow()
        recievedTime = currentTime.strftime('%Y-%m-%dT%H:%M:%S')
        stamp = int(time.mktime(currentTime.timetuple()))

        # Check destination standards support list
        conditions = [
            'key=\'standards',
            'AND',
            'userId'
            'IN',
            '(SELECT id FROM ' + User.tableName + ' WHERE username=' + self.DS.queryFormat(destination) + ')'
        ]
        q = self.DS.select(UserMeta, ' '.join(conditions))

        try:
            if len(q) > 0:
                standards = loads(q[0].value)
            else:
                raise AssertionError('Support list not found')
        except:
            standards = {
                'encryption': ['0'],
                'hashing': ['0']
            }

        standard = {
            'encryption': standards.encryption[-1],
            'hashing': standards.hashing[-1]
        }

        # Hash message
        hash = self.SS.hash(rawMsg, standard['hashing'])

        # Generate new message model
        msg = Message(
            None,
            username,
            destination,
            request['message'],
            request['stamp'],
            standard['encryption'],
            standard['hashing'],
            self.SS.hash(request['message']),
            None
        )

        # Encrypt message
        if int(standard['encryption']) > 0:
            try:
                user = self.DS.select(User, 'username=' + self.DS.queryFormat(destination))[0]
                for entryName, entryType in msg.tableSchema:
                    if entryName not in self.noEncrypt:
                        self.SS.encrypt(getattr(msg, entryName), standard['encryption'], key=user.publicKey)
            except IndexError:
                pass

        # Store message in db
        msgId = self.DS.insert(msg)

        # Generate message metadata for relay
        msgMetaTime = MessageMeta(None, msgId, 'recievedTime', recievedTime)
        msgMetaStatus = MessageMeta(None, msgId, 'relayAction', 'broadcast')
        self.DS.insertMany(msgMetaTime + msgMetaStatus)              

        msg = Message.deserialize(request)

        msgId = self.DS.insert(msg)

        try:
            if request['destination'] not in self.MS.data['pushRequests']:
                self.MS.data['pushRequests'].append(request['destination'])
        except KeyError:
            self.MS.data['pushRequests'] = [request['destination']]

        return '0'