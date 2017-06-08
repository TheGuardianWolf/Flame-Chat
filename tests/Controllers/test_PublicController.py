from tests.ServiceFactory import factory
from app import Globals
from app.Controllers.PublicController import PublicController
from app.Models.AuthModel import Auth


class TestPublicController(object):
    def __setup(self, tmpdir):
        services = factory(tmpdir)
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RequestService']
        self.DS = services['DatabaseService']
        self.MS = services['MemoryService']
    
    def test_listAPI(self, tmpdir):
        self.__setup(tmpdir)
        (status, response) = self.RS.get('http://localhost' + ':' + str(Globals.publicPort), '/listAPI')
        lines = response.read().splitlines()

        assert status == 200
        assert len(lines) > 2
        assert lines[-2].split(' ')[0] == 'Encryption'
        assert lines[-1].split(' ')[0] == 'Hashing'
        
    def test_ping(self):
        pass

    def test_recieveMessage(self):
        pass

    def test_getPublicKey(self):
        pass

    def test_handshake(self):
        pass
