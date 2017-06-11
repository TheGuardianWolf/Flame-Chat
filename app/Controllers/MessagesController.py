import cherrypy
from time import gmtime, strftime, time as getTime
from calendar import timegm
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
        self.noEncrypt = ['id', 'sender', 'destination', 'encryption']

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
                'AND',
                'id',
                'IN',
                '(SELECT messageId FROM ' + MessageMeta.tableName + ' WHERE key=\'relayAction\' AND (value=\'send\' OR value=\'broadcast\'))'
            ]
            toSend = self.DS.select(Message, ' '.join(conditions))
            pushList.append(toSend)

        # Helper function to push to individual users
        def push(messageList):
            pool = ThreadPool(processes=50)
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
        try:
            reachableUsers = self.MS.data['reachableUsers']
        except KeyError:
            reachableUsers = []

        if relayTo is None:
            # Find user entry
            try:
                for user in reachableUsers:
                    if message.destination == user.username:
                        destination = user
            except KeyError:
                pass

        if destination is not None:
            # Send the message if destination is not local
            if not destination.ip == self.LS.ip:
                # Check destination standards support list
                conditions = [
                    'key=\'standards\'',
                    'AND',
                    'userId',
                    'IN',
                    '(SELECT id FROM ' + User.tableName + ' WHERE username=' + self.DS.queryFormat(destination.username) + ')'
                ]
                q = self.DS.select(UserMeta, ' '.join(conditions))

                try:
                    if len(q) > 0:
                        standards = loads(q[0].value)

                        if 'encryption' not in standards:
                            standards['encryption'] = ['0']

                        if 'hashing' not in standards:
                            standards['hashing'] = ['0']
                    else:
                        raise AssertionError('Support list not found')
                except (ValueError, AssertionError):
                    standards = {
                        'encryption': ['0'],
                        'hashing': ['0']
                    }

                standard = {
                    'encryption': standards['encryption'][-1],
                    'hashing': standards['hashing'][-1]
                }

                # Hash message
                hash = self.SS.hash(message.message, standard['hashing'])

                # Update message model
                message.hashing = standard['hashing']
                message.hash = hash

                # Encrypt
                if int(standard['encryption']) > 0:
                    try:
                        for entryName, entryType in message.tableSchema:
                            if entryName not in self.noEncrypt:
                                value = getattr(message, entryName)
                                if value is not None:
                                    encValue = self.SS.encrypt(value, standard['encryption'], key=destination.publicKey)
                                    setattr(message, entryName, encValue)
                        message.encryption = standard['encryption']
                    except IndexError:
                        pass

                payload = message.serialize()
                del payload['id']

                for key, value in payload.items():
                    if value is None:
                        del payload[key]

                (status, response) = self.RS.post('http://' + str(destination.ip) + ':' + str(destination.port), '/receiveMessage', payload)
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
            self.sendMessage(params[1], relayTo=params[0])
        pool.map(delegate, paramList)
            

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self, since=None):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        if since is not None:
            try:
                timeSince = float(since)
            except ValueError:
                raise cherrypy.HTTPError(400, 'Malformed time.')

        try:
            streamEnabled = cherrypy.session['streamEnabled']
        except KeyError:
            streamEnabled = False

        username = cherrypy.session['username']

        cherrypy.session.release_lock()
        if not streamEnabled:
            if self.checkTiming(self.MS.data, 'lastRelayMessageSend', 300):
                self.relayMessages()

        conditions = [
            'sender=' + self.DS.queryFormat(username),
            'OR',
            'destination=' + self.DS.queryFormat(username)
        ]
        q = self.DS.select(Message, ' '.join(conditions))
            
        returnObj = []

        removeQueue = []
        markStoreQueue = []

        for i in range(0, len(q)):
            inbound = q[i].destination == username
            try:
                # Run checks on inbound messages
                if inbound:
                    # Decrypt if encrypted
                    if q[i].encryption is not None and int(q[i].encryption) > 0:
                        for entryName, entryType in q[i].tableSchema:
                            if entryName not in self.noEncrypt:
                                try:
                                    value = getattr(q[i], entryName)
                                    if value is not None:
                                        rawValue = self.SS.decrypt(getattr(q[i], entryName), q[i].encryption)
                                        setattr(q[i], entryName, rawValue)
                                except TypeError:
                                    raise ValueError('Cannot decrypt')

                    # Check if message is recent
                    if since is not None:
                        if float(q[i].stamp) <= float(since):
                            continue

                    # Check hashes of inbound
                    if q[i].hashing is not None and int(q[i].hashing) > 0:
                        if not self.SS.hash(q[i].message, q[i].hashing) == q[i].hash:
                            raise ValueError('Hashes do not match')

                    # Check for inbound duplicates
                    for msg in markStoreQueue:
                        if self.duplicateCheck(msg, q[i]):
                            raise ValueError('Duplicate message')

                    # Mark store if inbound and marked otherwise
                    if (q[i].destination == username):
                        markStoreQueue.append(q[i])

                else:
                    # Check if message is recent
                    if since is not None:
                        if float(q[i].stamp) <= float(since):
                            continue

                # Store object to be returned
                returnObj.append(q[i].serialize())
            except ValueError:
                removeQueue.append(q[i])
                continue

            # Process mark-stores
            self.upsertMessageMeta('relayAction', 'store', markStoreQueue)
            
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

        if not self.checkObjectKeys(request, ['destination', 'message']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')

        destination = request['destination']
        username = cherrypy.session['username']
        cherrypy.session.release_lock()

        currentTime = getTime()
        stamp = '{0:.3f}'.format(currentTime)

        # Generate new message model
        msg = Message(
            None,
            username,
            destination,
            request['message'],
            stamp
        )

        # Store message in db
        msgId = self.DS.insert(msg)

        # Generate message metadata for relay
        msgMetaTime = MessageMeta(None, msgId, 'recievedTime', stamp)
        msgMetaStatus = MessageMeta(None, msgId, 'relayAction', 'broadcast')
        self.DS.insertMany([msgMetaTime, msgMetaStatus])

        msg = Message.deserialize(request)

        try:
            if request['destination'] not in self.MS.data['pushRequests']:
                self.MS.data['pushRequests'].append(request['destination'])
        except KeyError:
            self.MS.data['pushRequests'] = [request['destination']]

        return '0'