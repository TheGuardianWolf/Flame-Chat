import os
import inspect
import app

# Values for server paths
# appRoot = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
appRoot = os.path.dirname(inspect.getfile(app))
appConfigRoot = os.path.join(appRoot, 'Config')
webRoot = os.path.join(appRoot, 'wwwroot')
loginRoot = r'http://cs302.pythonanywhere.com'

# Values for public server
publicPort = 10101

# Values for ip location
universityDesktop = '10.103.0.0'
universityWifi = '172.23.0.0'

# Values for encryption
privateKeyPath = os.path.join(appRoot, 'Data', 'key')
publicKeyPath = os.path.join(appRoot, 'Data', 'key.pub')
salt = 'COMPSYS302-2017'
serverKey = '150ecd12d550d05ad83f18328e536f53'
serverAESBlockSize = 16
serverAESPadding = ' '

# Values for data/storage
dbPath = os.path.join(appRoot, 'Data', 'entity.db')

# Values for standards support
standards = {
    'encryption': ['0', '3'],
    'hashing': ['0', '1', '3']
}
