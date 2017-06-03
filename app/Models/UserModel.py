from app.Models.__Model import __Model

class User(object):
    tableName = 'users'
    tableSchema = [
        ('id', 'integer primary key'),
        ('username', 'text'),
        ('ip', 'text'),
        ('location', 'integer'),
        ('port', 'integer'),
        ('lastLogin', 'integer'),
        ('publicKey', 'text')
    ]

    def __init__(self, *args):
        super(Auth, self).__init__(*args)
