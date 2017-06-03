from app.Models.__Model import __Model

class Message(__Model):
    tableName = 'messages'
    tableSchema = [
        ('id', 'integer primary key'),
        ('timestamp', 'text'),
        ('sender', 'text'),
        ('recipient', 'text'),
        ('text', 'text')
    ]

    def __init__(self, *args):
        super(Message, self).__init__(*args)
