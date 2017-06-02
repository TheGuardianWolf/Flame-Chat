import os
import inspect

# Values for server paths
appRoot = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
webRoot = os.path.join(appRoot, 'wwwroot')
loginRoot = r'http://cs302.pythonanywhere.com'

# Values for public server
publicPort = 8080

# Values for ip location
universityDesktop = '10.103.0.0'
universityWifi = '172.23.0.0'
universityExternalIP = '1.1.1.1'

# Values for encryption
privateKeyPath = os.path.join(appRoot, 'data', 'key')
publicKeyPath = os.path.join(appRoot, 'data', 'key.pub')
salt = 'COMPSYS302-2017'
serverKey = '150ecd12d550d05ad83f18328e536f53'
serverAESBlockSize = 16
serverAESPadding = ' '

# Values for data/storage
dbPath = os.path.join(appRoot, 'data', 'entity.db')