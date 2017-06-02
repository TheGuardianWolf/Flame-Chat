import sqlite3
import os
import Globals
from app.Models.UserModel import User
from app.Models.AuthModel import Auth

class DatabaseService(object):
    def __init__(self, dbPath):
        self.dbPath = dbPath
        self.__checkDB()

    def __checkDB(self):
        if not os.path.isfile(self.dbPath):
            models = [User, Auth]
            queries =  []
            command = 'CREATE TABLE IF NOT EXISTS'
            for model in models:
                args = []
                try:
                    if model.tableName is not None:
                        table = model.tableName
                        for item in model.tableSchema:
                            args.append(' '.join(item))
                except AttributeError:
                    print "Warning: " + str(model) + " does not have an associated table in the database."
                    continue
                queries.append(' '.join([command, table, '(' + ', '.join(args) + ')']))
            self.__query(queries)
            print 'Created new database at ' + self.dbPath
        else:
            print 'Using database found at ' + self.dbPath

    def __query(self, queries, fetch=False):
        connection = sqlite3.connect(self.dbPath)
        db = connection.cursor()
        returnVals = []

        for query in queries:
            db.execute(query)
            if fetch:
                returnVals.append(db.fetchall())
            else:
                returnVals.append(db.lastrowid)

        connection.commit()
        connection.close()
        return returnVals

    def insertMany(self, modelList):
        command = 'INSERT INTO'
        queries = []
        entryList = []
        for model in modelList:
            values = []
            # Potential AttributeError here from a model with no tableSchema or tableName
            for value in model.tableSchema:
                values.append(getattr(model, value[0]))
            entriesList.append((model.tableName, values))

        for entry in entriesList:
            queries.append(' '.join(
                [command, entry[0], 'VALUES', '(' + ','.join(entry[1]) + ')']
            ))

        return self.__query(queries)

    def insert(self, model):
        return self.insertMany([model])[0]

    def selectMany(self, modelList, conditionList=None):
        command = 'SELECT'
        queries = []

        for i in range(0, len(modelList)):
            model = modelList[i]
            queryList = [command, '*', 'FROM', model.tableName]
            if condtionList is not None and condition is not None:
                queryList.append('WHERE')
                queryList.append(conditionList[i])
            queries.append(' '.join(queryList))

        fetched = self.__query(queries, fetch=True)

        for i in range(0, len(fetched)):
            model = modelList[i]
            entries = fetched[i]
            for j in range(0, len(entries)):
                entries[j] = model(*entries[j])

