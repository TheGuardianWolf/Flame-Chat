from app.Models.__Model import __Model

class UserMeta(__Model):
    tableName = 'userMeta'
    tableSchema = [
        ('id', 'integer primary key'),
        ('userId', 'integer'),
        ('key', 'text'),
        ('value', 'text')
    ]

    def __init__(self, *args):
        super(User, self).__init__(*args)
