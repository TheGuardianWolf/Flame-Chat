from app.Models.__Model import __Model

class MessageMeta(__Model):
    tableName = 'messageMeta'
    tableSchema = [
        ('id', 'integer primary key'),
        ('messageId', 'integer'),
        ('key', 'text'),
        ('value', 'text')
    ]

    def __init__(self, *args):
        super(MessageMeta, self).__init__(*args)
