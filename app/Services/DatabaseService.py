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
                values = []
                try:
                    if model.tableName is not None:
                        table = model.tableName
                        for item in model.tableSchema:
                            values.append(' '.join(item))
                except AttributeError:
                    print "Warning: " + str(model) + " does not have an associated table in the database."
                    continue
                queries.append(' '.join([command, table, self.__bracketJoin(',', values)]))
            self.query(queries)
            print 'Created new database at ' + self.dbPath
        else:
            print 'Using database found at ' + self.dbPath

    def __queryFormatItem(self, item):
        if item is None:
            items[index] = 'NULL'
        else:
            items[index] = str(items[index])

    def __bracketJoin(self, joint, list):
        return '(' + joint.join(list) + ')'

    def query(self, queries, fetch=False):
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
        for model in modelList:
            entryNames = []
            entryValues = []
            for entry in model.tableSchema:
                entryNames.append(entry[0])
                entryValues.append(self.__queryFormatItem(getattr(model, entry[0])))
            queries.append(' '.join(
                [
                    command, 
                    modelList[i].tableName, 
                    self.__bracketJoin(',', entryNames), 
                    'VALUES', 
                    self.__bracketJoin(',', entryValues)
                ]
            ))
            

        return self.query(queries)

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

        fetched = self.query(queries, fetch=True)
        newModelsList = []

        for i, entries in enumerate(fetched):
            model = modelList[i]
            newModels = []
            for j, entry in enumerate(entries):
                newModels.append(model(*entries[j]))
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

        return self.query(queries)

    def delete(self, model, condition):
        try:
            return self.deleteMany([model], [condition])[0]
        except IndexError:
            return None

    def updateMany(self, modelList, conditionList):
        command = 'UPDATE'
        queries = []

        for i, model in enumerate(modelList):
            condition = conditionList[i]
            if condition is not None:
                queryParts = [command, model.tableName, 'SET']
                entries = []
                for entry in model.tableSchema:
                    entries.append(entry[0] + ' = ' + self.__queryFormatItem(getattr(model, entry[0])))
                queryParts.append(','.join(entries))
                queryParts.append('WHERE')
                queryParts.append(condition)
                queries.append(' '.join(queryParts))

        return self.query(queries)

    def update(self, model, condition):
        try:
            return self.updateMany([model], [condition])[0]
        except IndexError:
            return None
