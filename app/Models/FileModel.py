from app.Models.__Model import __Model

class File(__Model):
    tableName = 'files'
    tableSchema = [
        ('id', 'integer primary key'),
        ('fileId', 'text'),
        ('recievedTime', 'text'),
        ('sender', 'text'),
        ('destination', 'text'),
        ('file', 'text'),
        ('filename', 'text'),
        ('content_type', 'text'),
        ('stamp', 'text'),
        ('encryption', 'text'),
        ('hashing', 'text'),
        ('hash', 'text'),
        ('decryptionKey', 'text')
    ]

    def __init__(self, *args):
        super(File, self).__init__(*args)
