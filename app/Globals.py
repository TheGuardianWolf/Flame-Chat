import os
import inspect

# Values for server paths
appRoot = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
webRoot = os.path.join(appRoot, 'wwwroot')
loginRoot = r'cs302.pythonanywhere.com'

# Values for encryption
privateKeyPath = os.path.join(appRoot, 'data', 'key')
pubKeyPath = os.path.join(appRoot, 'data', 'key.pub')
salt = 'COMPSYS302-2017'
serverKey = '150ecd12d550d05ad83f18328e536f53'
serverAESBlockSize = 16
serverAESPadding = ' '

# Values for data/storage
dbPath = os.path.join(Globals.appRoot, 'data', 'entity.db')