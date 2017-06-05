import cherrypy
from datetime import datetime
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.MessageModel import Message
from app.Models.MessageMetaModel import MessageMeta
from app.Models.UserModel import User
from app.Models.UserMetaModel import UserMeta
from json import loads, dumps
from binascii import unhexlify

class MessagesController(__Controller):
    def __init__(self, services):
        super(MessagesController, self).__init__(services)
        self.noEncrypt = ['sender', 'destination', 'encryption', 'encoding']

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
            
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self, target, since=None):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')
        username = cherrypy.session['username']
        cherrypy.session.release_lock()
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
                # Check encoding
                if str(q[i].encoding) in Globals.standards.encoding:
                    raise ValueError('Encoding not supported')

                # Decrypt if encrypted
                if int(q[i].encryption) > 0:
                    for entryName, entryType in q[i].tableSchema:
                        if entryName not in self.noEncrypt:
                            self.SS.decrypt(getattr(q[i], entryName), q[i].encryption)

                # Unencode
                q[i].message = self.decodeMessage(q[i].message, q[i].encoding)

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

                # Encode utf-8 for local transmission
                q[i].message = self.encodeMessage(q[i].message, '2')

                # Store object to be returned
                returnObj.append(q[i].serialize()) 
            except ValueError:
                removeQueue.append(q[i])
                continue

            # Process mark-reads
            insertList = []
            updateList = []
            for msg in markReadQueue:
                q = self.DS.select(MessageMeta, 'messageId=' + self.DS.queryFormat(msg.id) + ' AND key=\'relayStatus\'')
                if len(q) > 0:
                    updateList.append(MessageMeta(q[0].id, msg.id, 'relayStatus', 'sent'))
                else:
                    insertList.append(MessageMeta(None, msg.id, 'relayStatus', 'sent'))
            if len(updateList) > 0:
                self.DS.updateMany(updateList)
            if len(insertList) > 0:
                self.DS.insertMany(insertList)
            
            # Process removals
            modelsList = []
            conditionsList = []
            for msg in removeQueue:
                modelsList.append(Message)
                conditionsList.append('id=' + self.DS.queryFormat(msg.id))
                modelsList.append(MessageMeta)
                conditionsList.append('messageId=' + self.DS.queryFormat(msg.id))
            self.DS.deleteMany(modelsList, conditionsList)

        return returnObj


    @cherrypy.expose
    @cherrypy.tools.json_in()
    def post(self):
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
                # Assume we already sorted the values in the db on entry
                standard = {
                    'encryption': standards.encryption[-1],
                    'encoding': standards.encoding[-1],
                    'hashing': standards.hashing[-1]
                }
        except:
            standard = {
                'encryption': '0',
                'encoding': '0',
                'hashing': '0'
            }

        # Find destination's encryption key and run test
        if int(standard['encryption']) > 2:
            try:
                user = self.DS.select(User, 'username=' + self.DS.queryFormat(destination))[0]
                encryptionKey = user.publicKey
                self.SS.encrypt('a', '3', key=unhexlify(encryptionKey))
            except:
                standard['encryption'] = '0'

        rawMsg = request['message'].decode('utf-8', 'replace')

        # Encode message
        if int(standard['encryption']) == 3:
            text = self.encodeMessage(rawMsg, '0')
            standard['encoding'] = 0
        else:
            text = self.encodeMessage(rawMsg, standard['encoding'])

        # Hash message
        hash = self.SS.hash(rawMsg, standard['hashing'])

        # Generate new message model
        msg = Message(
            None,
            username,
            destination,
            text,
            request['stamp'],
            '0',
            standard['encoding'],
            standard['encryption'],
            standard['hashing'],
            self.SS.hash(text),
            None
        )

        # Encrypt message
        if int(standard['encryption']) > 0:
            for entryName, entryType in msg.tableSchema:
                if entryName not in self.noEncrypt:
                    self.SS.encrypt(getattr(msg, entryName), standard['encryption'], key=encryptionKey)

        # Store message in db
        msgId = self.DS.insert(msg)

        # Generate message metadata for relay
        msgMetaTime = MessageMeta(None, msgId, 'recievedTime', recievedTime)
        msgMetaStatus = MessageMeta(None, msgId, 'relayStatus', 'new')
        self.DS.insertMany(msgMetaTime + msgMetaStatus)              

        msg = Message.deserialize(request)

        msgId = self.DS.insert(msg)

        try:
            self.MS.data['pushRequests'].append(request['destination'])
        except KeyError:
            self.MS.data['pushRequests'] = [request['destination']]

        return '0'