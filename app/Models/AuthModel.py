from app.Models.__Model import __Model

class Auth(__Model):
    tableName = 'auth'
    tableSchema = [
        ('id', 'integer primary key'),
        ('username', 'text'),
        ('passhash', 'text')
    ]

    def __init__(self, *args):
        super(Auth, self).__init__(*args)
