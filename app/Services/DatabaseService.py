import sqlite3
import os
import Globals
from app.Models.UserModel import User
from app.Models.AuthModel import Auth

class DatabaseService():
    def __init__(self):
        self.__checkDB__()

    def __checkDB__(self):
        if not os.path.isfile(DatabaseService.dbPath):
            print 'Creating new database at ' + DatabaseService.dbPath
            connection = sqlite3.connect(DatabaseService.dbPath)
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
                    continue
            connection.commit()
            connection.close()
        else:
            print 'Using database found at ' + DatabaseService.dbPath