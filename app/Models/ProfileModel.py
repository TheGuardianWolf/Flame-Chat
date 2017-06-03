from app.Models.__Model import __Model

class Profile(__Model):
    tableName = 'profiles'
    tableSchema = [
        ('id', 'integer primary key'),
        ('userId', 'integer'),
        ('fullname', 'text'),
        ('position', 'text'),
        ('description', 'text'),
        ('location', 'text'),
        ('picture', 'integer')
    ]

    def __init__(self, *args):
        super(Profile, self).__init__(*args)
