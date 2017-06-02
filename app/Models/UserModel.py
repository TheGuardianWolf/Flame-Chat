class User(object):
    tableName = 'users'
    tableSchema = [
        ('id', 'integer primary key'),
        ('username', 'text'),
        ('ip', 'text'),
        ('port', 'integer'),
        ('lastLogin', 'integer'),
        ('publicKey', 'string')
    ]

    def __init__(self, id, username, location, ip, port, lastLogin, publicKey):
        self.id = id
        self.username = username
        self.location = location
        self.ip = ip
        self.port = port
        self.lastLogin = lastLogin
        self.publicKey = publicKey
