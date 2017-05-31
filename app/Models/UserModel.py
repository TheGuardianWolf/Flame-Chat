class User():
    tableName = 'users'
    tableSchema = [
        ('id', 'integer primary key'),
        ('username', 'text'),
        ('ip', 'text')
    ]

    def __init__(self, id, username, ip):
        self.id = id
        self.username = username
        self.ip = ip
