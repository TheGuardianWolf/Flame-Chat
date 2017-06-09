from app.Models.__Model import __Model

class FileMeta(__Model):
    tableName = 'fileMeta'
    tableSchema = [
        ('id', 'integer primary key'),
        ('fileId', 'integer'),
        ('key', 'text'),
        ('value', 'text')
    ]

    def __init__(self, *args):
        super(FileMeta, self).__init__(*args)
