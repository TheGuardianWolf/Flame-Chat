class Auth():
    tableName = 'auth'
    tableSchema = [
        ('id', 'integer primary key'),
        ('username', 'text'),
        ('passhash', 'text')
    ]

    def __init__(self, username, passhash):
        self.username = username
        self.passhash = passhash
