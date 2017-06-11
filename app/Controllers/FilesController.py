        self.noEncrypt = ['id', 'sender', 'destination', 'encryption']
        try:
            reachableUsers = self.MS.data['reachableUsers']
        except KeyError:
            reachableUsers = []
            try:
                for user in reachableUsers:
                    if file.destination == user.username:
                        destination = user
            except KeyError:
                pass
            # Send the file if destination is not local
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


                for key, value in payload.items():
                    if value is None:
                        del payload[key]

            self.sendFile(params[1], relayTo=params[0])
        if since is not None:
            try:
                timeSince = float(since)
            except ValueError:
                raise cherrypy.HTTPError(400, 'Malformed time.')

        conditions = [
            'sender=' + self.DS.queryFormat(username),
            'OR',
            'destination=' + self.DS.queryFormat(username)
        ]
        q = self.DS.select(File, ' '.join(conditions))
        markStoreQueue = []
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

                        if not self.SS.hash(q[i].file, q[i].hashing) == q[i].hash:
                    for file in markStoreQueue:
                        markStoreQueue.append(q[i])

                else:
                    # Check if message is recent
                    if since is not None:
                        if float(q[i].stamp) <= float(since):
                            continue
            self.upsertFileMeta('relayAction', 'store', markStoreQueue)
        destination = request['destination']
            stamp
        self.DS.insertMany([fileMetaTime, fileMetaStatus])              
        return '0'