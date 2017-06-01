class Auth():
    tableName = 'auth'
    tableSchema = [
        ('id', 'integer primary key'),
        ('username', 'text'),
        ('passhash', 'text')
    ]

    def __init__(self, id, username, passhash):
        self.id = id
        self.username = username
        self.passhash = passhash
