import os
import inspect

appRoot = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
webRoot = os.path.join(appRoot, 'wwwroot')