import sqlite3
from .. import globals


class DatabaseService():
    def __init__(self):
        self.connection = sqlite3.connect(globals.appRoot + '/data/entity.db')
