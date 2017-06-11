import os
from sqlite3 import IntegrityError, connect, OperationalError
from time import sleep
from app import Globals
from app.Models.AuthModel import Auth
from app.Models.MessageModel import Message
from app.Models.MessageMetaModel import MessageMeta
from app.Models.UserModel import User
from app.Models.UserMetaModel import UserMeta
from app.Models.ProfileModel import Profile
from app.Models.FileModel import File
from app.Models.FileMetaModel import FileMeta

class DatabaseService(object):
    def __init__(self, dbPath):
        self.__busy = False
        self.dbPath = dbPath
        self.__checkDB()
        

    def __checkDB(self):
        if not os.path.isfile(self.dbPath):
            models = [User, UserMeta, Auth, Message, MessageMeta, Profile, File, FileMeta]
            queries =  []
            command = 'CREATE TABLE IF NOT EXISTS'
            for model in models:
                values = []
                try:
                    if model.tableName is not None:
                        table = model.tableName
                        for item in model.tableSchema:
                            values.append(' '.join(item))
                except AttributeError:
                    print "Warning: " + str(model) + " does not have an associated table in the database."
                    continue
                queries.append(' '.join([command, table, self.bracketJoin(',', values)]))
            self.queryMany(queries)
            print 'Created new database at ' + self.dbPath
        else:
            print 'Using database found at ' + self.dbPath

    def queryFormat(self, item):
        if item is None:
            return 'NULL'
        elif isinstance(item, basestring):
            return '\'' + item.replace('\'', '\'\'') + '\''
        else:
            return unicode(item)

    def bracketJoin(self, joint, list):
        return '(' + joint.join(list) + ')'

    def queryMany(self, queries, fetch=False):
        while (self.__busy):
            sleep(0.5)
        self.__busy = True;
        connection = connect(self.dbPath)
        db = connection.cursor()
        returnVals = []

        for query in queries:
            #try:
            db.execute(query)
            #except IntegrityError:
            #    raise IntegrityError('datatype mismatch in query: ' + query)
            #except OperationalError:
            #    raise OperationalError('Error in: ' + query)

            if fetch:
                returnVals.append(db.fetchall())
            else:
                returnVals.append(db.lastrowid)

        connection.commit()
        connection.close()
        self.__busy = False;
        return returnVals

    def query(self, query, fetch=False):
        try:
            return self.queryMany([query], fetch)[0]
        except IndexError:
            return None

    def insertMany(self, modelList):
        command = 'INSERT INTO'
        queries = []
        for i, model in enumerate(modelList):
            entryNames = []
            entryValues = []
            for entry in model.tableSchema:
                entryNames.append(entry[0])
                entryValues.append(self.queryFormat(getattr(model, entry[0])))
            queries.append(' '.join(
                [
                    command, 
                    modelList[i].tableName, 
                    self.bracketJoin(',', entryNames), 
                    'VALUES', 
                    self.bracketJoin(',', entryValues)
                ]
            ))
        return self.queryMany(queries)

    def insert(self, model):
        try:
            return self.insertMany([model])[0]
        except IndexError:
            return None

    def selectMany(self, modelList, conditionList=None):
        command = 'SELECT'
        queries = []

        for i, model in enumerate(modelList):
            queryParts = [command, '*', 'FROM', model.tableName]
            if conditionList is not None:
                condition = conditionList[i]
                if condition is not None:
                    queryParts.append('WHERE')
                    queryParts.append(condition)
            queries.append(' '.join(queryParts))

        fetched = self.queryMany(queries, fetch=True)
        newModelsList = []

        for i, entries in enumerate(fetched):
            model = modelList[i]
            newModels = []
            for j, entry in enumerate(entries):
                typedModelArgs = []
                newModels.append(model.deserialize(entries[j]))
            newModelsList.append(newModels)

        return newModelsList

    def select(self, model, condition=None):
        try:
            return self.selectMany([model], [condition])[0]
        except IndexError:
            return None

    def deleteMany(self, modelList, conditionList):
        command = 'DELETE FROM'
        queries = []

        for i, model in enumerate(modelList):
            condition = conditionList[i]
            if condition is not None:
                queryParts = [command, model.tableName, 'WHERE', condition]
                queries.append(' '.join(queryParts))

        return self.queryMany(queries)

    def delete(self, model, condition):
        try:
            return self.deleteMany([model], [condition])[0]
        except IndexError:
            return None

    def updateMany(self, modelList):
        command = 'UPDATE'
        queries = []

        for i, model in enumerate(modelList):
            queryParts = [command, model.tableName, 'SET']
            entries = []
            for entry in model.tableSchema:
                entries.append(entry[0] + ' = ' + self.queryFormat(getattr(model, entry[0])))
            queryParts.append(','.join(entries))
            queryParts.append('WHERE')
            queryParts.append('id=' + self.queryFormat(model.id))
            queries.append(' '.join(queryParts))

        return self.queryMany(queries)

    def update(self, model):
        try:
            return self.updateMany([model])[0]
        except IndexError:
            return None
