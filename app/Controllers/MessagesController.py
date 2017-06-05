import cherrypy
from datetime import datetime
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.MessageModel import Message
from app.Models.MessageMetaModel import MessageMeta
from json import loads, dumps

class MessagesController(__Controller):
    def __init__(self, services):
        super(MessagesController, self).__init__(services)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self, target, since=None):
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')
        
        if since is None:
            conditions = [
                '(sender=' + self.DS.queryFormat(cherrypy.session['username']),
                'AND'
                'destination=' + self.DS.queryFormat(target) + ')',
                'OR',
                '(sender=' + self.DS.queryFormat(target),
                'AND'
                'destination=' + self.DS.queryFormat(cherrypy.session['username']) + ')'
            ]
            q = self.DS.select(Message, ' '.join(conditions))
        else:
            try:
                timeString = datetime.strptime(since.split('.')[0], "%Y-%m-%dT%H:%M:%SZ" )
            except (ValueError, IndexError) as e:
                raise cherrypy.HTTPError(400, 'Malformed time.')
            conditions = [
                '(sender=' + self.DS.queryFormat(cherrypy.session['username']),
                'AND'
                'destination=' + self.DS.queryFormat(target) + ')',
                'OR',
                '(sender=' + self.DS.queryFormat(target),
                'AND'
                'destination=' + self.DS.queryFormat(cherrypy.session['username']) + ')',
                'AND'
                'id',
                'IN',
                '(SELECT messageId FROM ' + MessageMeta.tableName + ' WHERE key=\'recievedTime\' AND value > \'' + timeString + '\')'
            ]
            q = self.DS.select(Message, ' '.join(conditions))

        decryptedObjs = []
        returnObj = []

        removeQueue = []
        markReadQueue = []

        for i in range(0, len(q)):
            qObj = q[i].serialize()
            
            try:
                # Decrypt if encrypted
                if (int(q[i].encryption) > 0):
                    for entryName, entryType in q[i].tableSchema:
                        if entryName not in ['encryption', 'encoding']:
                            self.SS.decrypt(getattr(q[i], entryName))
                # Check hashes
                if (int(q[i].hashing) > 0):
                    if not self.SS.hash(q[i].message, q[i].hashing, sender=q[i].sender) == q[i].hash:
                        raise ValueError('Hashes do not match')
                # Check for duplicates
            except ValueError:
                removeQueue.append(q[i])
                continue
            
            # Mark read
            markReadQueue.append(q[i])
            
            

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

        if not self.checkObjectKeys(request, ['destination', 'message']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')

        request['encoding'] = unicode(encoding)

        recievedTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        msg = Message.deserialize(request)

        msgId = self.DS.insert(msg)

        msgMetaTime = MessageMeta(None, msgId, 'recievedTime', recievedTime)
        msgMetaStatus = MessageMeta(None, msgId, 'relayStatus', 'new')

        self.DS.insertMany([msgMeta, msgMetaStatus])

        try:
            self.MS.data['pushRequests'].append(request['destination'])
        except KeyError:
            self.MS.data['pushRequests'] = [request['destination']]

        return '0'