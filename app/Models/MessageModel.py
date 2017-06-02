class Message(object):
    tableName = 'messages'
    tableSchema = [
        ('id', 'integer primary key'),
        ('timestamp', 'text'),
        ('sender', 'text'),
        ('recipient', 'text'),
        ('text', 'text')
    ]

    def __init__(self, id, timestamp, sender, recipient, text):
        self.id = id
        self.timestamp = timestamp
        self.sender = sender
        self.recipient = recipient
        self.text = text
