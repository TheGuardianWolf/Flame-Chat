from time import gmtime, strftime, time as getTime
from calendar import timegm
                'AND',
                payload = file.serialize()
                del payload['id']
                (status, response) = self.RS.post('http://' + str(destination.ip) + ':' + str(destination.port), '/receiveFile', payload)
    def get(self, since=None):
            #conditions = [
            #    '(sender=' + self.DS.queryFormat(username),
            #    'AND',
            #    'destination=' + self.DS.queryFormat(target) + ')',
            #    'OR',
            #    '(sender=' + self.DS.queryFormat(target),
            #    'AND',
            #    'destination=' + self.DS.queryFormat(username) + ')'
            #]
            #q = self.DS.select(File, ' '.join(conditions))
            q = self.DS.select(File, 'destination=' + self.DS.queryFormat(username))
                timeSince = timegm(gmtime(float(since)))
            except ValueError:
            #conditions = [
            #    '(sender=' + self.DS.queryFormat(username),
            #    'AND',
            #    'destination=' + self.DS.queryFormat(target) + ')',
            #    'OR',
            #    '(sender=' + self.DS.queryFormat(target),
            #    'AND',
            #    'destination=' + self.DS.queryFormat(username) + ')',
            #    'AND',
            #    'id',
            #    'IN',
            #    '(SELECT fileId FROM ' + FileMeta.tableName + ' WHERE key=\'recievedTime\' AND value > \'' + timeString + '\')'
            #]
                'destination=' + self.DS.queryFormat(username),
                'AND',
                '(SELECT fileId FROM ' + FileMeta.tableName + ' WHERE key=\'recievedTime\' AND CAST(value as REAL) > ' + '{0:.3f}'.format(timeSince) + ')'
                if q[i].encryption is not None and int(q[i].encryption) > 0:
                    if q[i].hashing is not None and int(q[i].hashing) > 0:
        if not self.checkObjectKeys(request, ['destination', 'file', 'filename', 'content_type']):
        currentTime = getTime()
        stamp = '{0:.3f}'.format(currentTime)
            'key=\'standards\'',
            'userId',
            stamp,
        fileMetaTime = FileMeta(None, fileId, 'recievedTime', stamp)