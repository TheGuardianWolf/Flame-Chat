import sqlite3
import os
import Globals
from app.Models.UserModel import User
from app.Models.AuthModel import Auth

class DatabaseService():
    def __init__(self):
        self.__checkDB()

    def __checkDB(self):
        if not os.path.isfile(Globals.dbPath):
            print 'Creating new database at ' + Globals.dbPath
            connection = sqlite3.connect(Globals.dbPath)
            db = connection.cursor()
            models = [User, Auth]
            for model in models:
                try:
                    command = 'CREATE TABLE IF NOT EXISTS'
                    table = model.tableName
                    args = []
                    for item in model.tableSchema:
                        args.append(' '.join(item))
                    db.execute(' '.join([command, table, '(' + ', '.join(args) + ')']))
                except AttributeError:
                    print "Warning: " + str(model) + " does not have an associated table in the database."
                    continue
            connection.commit()
            connection.close()
        else:
            print 'Using database found at ' + Globals.dbPath