from app.Models.__Model import __Model

class Message(__Model):
    tableName = 'messages'
    tableSchema = [
        ('id', 'integer primary key'),
        ('messageId', 'text'),
        ('sender', 'text'),
        ('destination', 'text'),
        ('message', 'text'),
        ('stamp', 'text'),
        ('markdown', 'text'),
        ('encoding', 'text'),
        ('encryption', 'text'),
        ('hashing', 'text'),
        ('hash', 'text'),
        ('decryptionKey', 'text')
    ]

    def __init__(self, *args):
        super(Message, self).__init__(*args)
