import cherrypy
from datetime import datetime

class __Controller(object):
    def __init__(self, services):
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RestfulService']
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

    def checkTiming(object, key, assertSecondsPassed):
        if key not in object or (datetime.now() - object[key]).seconds >= assertSecondsPassed:
            return True
        return False