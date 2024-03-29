import cherrypy
from datetime import datetime
from time import gmtime, strftime, time as getTime
from calendar import timegm
from multiprocessing.pool import ThreadPool
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.FileModel import File
from app.Models.FileMetaModel import FileMeta
from app.Models.UserModel import User
from app.Models.UserMetaModel import UserMeta
from json import loads, dumps

class FilesController(__Controller):
    def __init__(self, services):
        super(FilesController, self).__init__(services)
        self.noEncrypt = ['id', 'sender', 'destination', 'encryption']

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
                    aU = self.SS.cmpHash(''.join([u'>', unicode(a.file), unicode(a.stamp), u'<']))
                    bU = self.SS.cmpHash(''.join([u'>', unicode(b.file), unicode(b.stamp), u'<']))
                    if aU == bU:
                        return True
                    else:
                        return False
                except (ValueError, TypeError):
                    return False

    def upsertFileMeta(self, metaKey, metaValue, fileList):
        insertList = []
        updateList = []
        for file in fileList:
            q = self.DS.select(FileMeta, 'fileId=' + self.DS.queryFormat(file.id) + ' AND key=\'' + metaKey + '\'')
            if len(q) > 0:
                updateList.append(FileMeta(q[0].id, file.id, metaKey, metaValue))
            else:
                insertList.append(FileMeta(None, file.id, metaKey, metaValue))
        if len(updateList) > 0:
            self.DS.updateMany(updateList)
        if len(insertList) > 0:
            self.DS.insertMany(insertList)

    def deleteFiles(self, fileList):
        modelsList = []
        conditionsList = []
        for file in fileList:
            modelsList.append(File)
            conditionsList.append('id=' + self.DS.queryFormat(file.id))
            modelsList.append(FileMeta)
            conditionsList.append('fileId=' + self.DS.queryFormat(file.id))
        self.DS.deleteMany(modelsList, conditionsList)

    def pushFiles(self):
        pushList = []
        for username in self.MS.data['pushRequests']:
            conditions = [
                'destination=' + self.DS.queryFormat(username),
                'AND',
                'id',
                'IN',
                '(SELECT fileId FROM ' + FileMeta.tableName + ' WHERE key=\'relayAction\' AND (value=\'send\' OR value=\'broadcast\'))'
            ]
            toSend = self.DS.select(File, ' '.join(conditions))
            pushList.append(toSend)

        # Helper function to push to individual users
        def push(fileList):
            # Cherrypy servers limited to 10 concurrent requests per second
            pool = ThreadPool(processes=5)
            pool.map(self.sendFile, fileList)

        pool = ThreadPool(processes=50)
        pool.map(push, pushList)

    def relayFiles(self):
        self.MS.data['lastRelayFileSend'] = datetime.utcnow()
        conditions = [
            'id',
            'IN',
            '(SELECT fileId FROM ' + FileMeta.tableName + ' WHERE key=\'relayAction\' AND value=\'send\')'
        ]
        toSend = self.DS.select(File, ' '.join(conditions))
        conditions = [
            'id',
            'IN',
            '(SELECT fileId FROM ' + FileMeta.tableName + ' WHERE key=\'relayAction\' AND value=\'broadcast\')'
        ]
        toBroadcast = self.DS.select(File, ' '.join(conditions))

        pool = ThreadPool(processes=5)
        pool.map(self.sendFile, toSend)
        pool.map(self.broadcastFile, toBroadcast)

    def sendFile(self, file, relayTo=None):
        destination = relayTo
        try:
            reachableUsers = self.MS.data['reachableUsers']
        except KeyError:
            reachableUsers = []

        if relayTo is None:
            # Find user entry
            try:
                for user in reachableUsers:
                    if file.destination == user.username:
                        destination = user
            except KeyError:
                pass

        if destination is not None:
            # Send the file if destination is not local
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

                # Hash file
                hash = self.SS.hash(file.file, standard['hashing'])

                # Update file
                file.hashing = standard['hashing']
                file.hash = hash

                # Encrypt
                if int(standard['encryption']) > 0:
                    try:
                        for entryName, entryType in file.tableSchema:
                            if entryName not in self.noEncrypt:
                                value = getattr(file, entryName)
                                if value is not None:
                                    encValue = self.SS.encrypt(value, standard['encryption'], key=destination.publicKey)
                                    setattr(file, entryName, encValue)
                        file.encryption = standard['encryption']
                    except IndexError:
                        pass

                payload = file.serialize()
                del payload['id']

                for key, value in payload.items():
                    if value is None:
                        del payload[key]

                (status, response) = self.RS.post('http://' + str(destination.ip) + ':' + str(destination.port), '/receiveFile', payload)
            # Mark file action as store if direct send, else as send if relayed
            if relayTo is None:
                self.upsertFileMeta('relayAction', 'store', [file])
            else:
                # Should I still attempt direct send after relaying?
                # Currently, yes, as it's best not to rely on other relay nodes
                self.upsertFileMeta('relayAction', 'send', [file])
        return
                

    def broadcastFile(self, file):
        try:
            reachableUsers = self.MS.data['reachableUsers']
        except KeyError:
            reachableUsers = []
        
        reachableRemoteUsers = []
        
        # Filter out the local users from the broadcast list
        # Files with local user as destination and broadcast will be held indefinately
        for user in reachableUsers:
            if user.ip == self.LS.ip:
                if user.username == file.destination:
                    return
            else:
                reachableRemoteUsers.append(user)
    
        # Check if destination is on the broadcast list, and if so, change to direct send
        for user in reachableRemoteUsers:
            if file.destination == user.username:
                # Change to direct send
                return self.sendFile(file)
                
        paramList = []
        for user in reachableRemoteUsers:
            paramList.append((user, file))
        pool = ThreadPool(processes=25)
        # Can only use one argument with map, so use helper function to seperate parameters from a tuple
        def delegate(params):
            self.sendFile(params[1], relayTo=params[0])
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
            if self.checkTiming(self.MS.data, 'lastRelayFileSend', 300):
                self.relayFiles()
        
        conditions = [
            'sender=' + self.DS.queryFormat(username),
            'OR',
            'destination=' + self.DS.queryFormat(username)
        ]
        q = self.DS.select(File, ' '.join(conditions))

        returnObj = []

        removeQueue = []
        markStoreQueue = []

        for i in range(0, len(q)):
            inbound = q[i].destination == username
            try:
                # Run checks on inbound files
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
                                    cherrypy.log.error('Cannot decrypt file from ' + unicode(q[i].sender))
                                    raise ValueError('Cannot decrypt')

                    # Check if file is recent
                    if since is not None:
                        if float(q[i].stamp) <= float(since):
                            continue

                    # Check hashes of inbound
                    if q[i].hashing is not None and int(q[i].hashing) > 0:
                        if not self.SS.hash(q[i].file, q[i].hashing) == q[i].hash:
                            raise ValueError('Hashes do not match')

                    # Check for inbound duplicates
                    for file in markStoreQueue:
                        if self.duplicateCheck(file, q[i]):
                            raise ValueError('Duplicate file')

                    # Mark sent if inbound and unmarked
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

            # Process mark-reads
            self.upsertFileMeta('relayAction', 'store', markStoreQueue)
            
            # Process removals
            self.deleteFiles(removeQueue)

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

        if not self.checkObjectKeys(request, ['destination', 'file', 'filename', 'content_type']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')

        destination = request['destination']
        username = cherrypy.session['username']
        cherrypy.session.release_lock()

        currentTime = getTime()
        stamp = '{0:.3f}'.format(currentTime)

        # Generate new file model
        file = File(
            None,
            username,
            destination,
            request['file'],
            request['filename'],
            request['content_type'],
            stamp
        )

        # Store file in db
        fileId = self.DS.insert(file)

        # Generate file metadata for relay
        fileMetaTime = FileMeta(None, fileId, 'recievedTime', stamp)
        fileMetaStatus = FileMeta(None, fileId, 'relayAction', 'broadcast')
        self.DS.insertMany([fileMetaTime, fileMetaStatus])              

        file = File.deserialize(request)

        try:
            if request['destination'] not in self.MS.data['pushRequests']:
                self.MS.data['pushRequests'].append(request['destination'])
        except KeyError:
            self.MS.data['pushRequests'] = [request['destination']]

        return '0'
