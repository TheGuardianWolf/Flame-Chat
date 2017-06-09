import cherrypy
from datetime import datetime

class __Controller(object):
    def __init__(self, services):
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RequestService']
        self.DS = services['DatabaseService']
        self.MS = services['MemoryService']

    def isAuthenticated(self):
        try:
            if (cherrypy.session['authenticated'] == False):
                return False
            else:
                return True
        except KeyError:
            return False

    def checkTiming(self, object, key, assertSecondsPassed):
        if key not in object or object[key] is None or (datetime.utcnow() - object[key]).seconds >= assertSecondsPassed:
            return True
        return False

    def checkObjectKeys(self, obj, keys):
        for key in keys:
            try:
                if obj[key] == None:
                    return False
            except KeyError:
                return False
        return True