from tests.ServiceFactory import factory
from datetime import datetime
from time import time as getTime
from json import dumps, loads
from binascii import hexlify
from base64 import b64decode, b64decode
from app import Globals
from app.Controllers.PublicController import PublicController
from app.Models.UserModel import User
from app.Models.MessageModel import Message
from app.Models.MessageMetaModel import MessageMeta
from app.Models.FileModel import File
from app.Models.FileMetaModel import FileMeta
from app.Models.ProfileModel import Profile


class TestPublicController(object):
    def __setup(self):
        services = factory()
        self.LS = services['LoginService']
        self.SS = services['SecureService']
        self.RS = services['RequestService']
        self.DS = services['DatabaseService']
        self.MS = services['MemoryService']
    
    def test_listAPI(self, tmpdir):
        self.__setup()
        (status, response) = self.RS.get('http://localhost' + ':' + str(Globals.publicPort), '/listAPI')
        lines = response.read().splitlines()

        assert status == 200
        assert len(lines) > 2
        assert lines[-2].split(' ')[0] == 'Encryption'
        assert lines[-1].split(' ')[0] == 'Hashing'
        
    def test_ping(self, tmpdir):
        self.__setup()
        (status, response) = self.RS.get('http://localhost' + ':' + str(Globals.publicPort), '/ping', {'sender':'test'})
        assert status == 200
        assert response.read() == '0'

    def test_receiveMessage(self, tmpdir):
        self.__setup()
        testMessage = Message(
                None,
                'test',
                'testReceiver',
                'This is a test',
                int(getTime())
        )
        (status, response) = self.RS.post('http://localhost' + ':' + str(Globals.publicPort), '/receiveMessage', testMessage.serialize())
        assert status == 200
        assert response.read() == '0'
        testMessagesCondition = 'sender=\'test\' AND destination=\'testReceiver\''
        message = self.DS.select(Message, testMessagesCondition)[0]
        assert message.message == 'This is a test'
        metaRecieved = self.DS.select(MessageMeta, 'messageId=' + self.DS.queryFormat(message.id) + ' AND key=\'recievedTime\'')[0]
        metaAction = self.DS.select(MessageMeta, 'messageId=' + self.DS.queryFormat(message.id) + ' AND key=\'relayAction\'')[0]
        assert metaRecieved.value is not None
        assert metaAction.value == 'send'
        self.DS.delete(MessageMeta, 'messageId=' + self.DS.queryFormat(message.id))
        self.DS.delete(Message, 'id=' + self.DS.queryFormat(message.id))

    def test_getPublicKey(self, tmpdir):
        self.__setup()
        self.DS.insert(User(
            None,
            'test',
            '0.0.0.1',
            '2',
            '8080',
            int(getTime()),
            'abcd'
        ))
        (status, response) = self.RS.post('http://localhost' + ':' + str(Globals.publicPort), '/getPublicKey', {
            'sender': 'test',
            'profile_username': 'test'
        })
        assert status == 200
        r = loads(response.read())
        assert r['pubKey'] == 'abcd'
        self.DS.delete(User, 'username=' + self.DS.queryFormat('test'))

    def test_handshake(self, tmpdir):
        self.__setup()
        msg = self.SS.encrypt('testMessage', 3, key=hexlify(self.SS.publicKey.exportKey('DER')))
        (status, response) = self.RS.post('http://localhost' + ':' + str(Globals.publicPort), '/handshake', {
            'sender': 'test',
            'message': msg,
            'destination': 'test',
            'encryption': 3
        })
        assert status == 200
        r = loads(response.read())
        assert r['message'] == 'testMessage'

    def test_getProfile(self, tmpdir):
        self.__setup()
        testUser = User(
            None,
            'test'
        )
        userId = self.DS.insert(testUser)
        testProfile = Profile(
                None,
                userId,
                'Test User',
                None,
                None,
                None,
                None
        )
        profileId = self.DS.insert(testProfile)
        (status, response) = self.RS.post('http://localhost' + ':' + str(Globals.publicPort), '/getProfile', {
            'profile_username': 'test',
            'sender': 'test'
        })
        assert status == 200
        r = loads(response.read())
        assert r['fullname'] == 'Test User'
        self.DS.delete(User, 'id=' + self.DS.queryFormat(userId))
        self.DS.delete(Profile, 'id=' + self.DS.queryFormat(profileId))

    def receiveFile(self, tmpdir):
        self.__setup()
        testFile = File(
                None,
                'test',
                'test',
                b64encode('abcd'),
                'fileText.txt',
                'text/plain',
                int(getTime())
        )
        (status, response) = self.RS.post('http://localhost' + ':' + str(Globals.publicPort), '/receiveFile', testFile.serialize())
        assert status == 200
        assert response.read() == '0'
        testFileCondition = 'sender=\'test\' AND destination=\'testReceiver\''
        file = self.DS.select(Message, testFileCondition)[0]
        assert b64decode(file.file) == 'abcd'
        metaRecieved = self.DS.select(FileMeta, 'fileId=' + self.DS.queryFormat(file.id) + ' AND key=\'recievedTime\'')[0]
        metaAction = self.DS.select(FileMeta, 'fileId=' + self.DS.queryFormat(file.id) + ' AND key=\'relayAction\'')[0]
        assert metaRecieved.value is not None
        assert metaAction.value == 'send'
        self.DS.delete(FileMeta, 'fileId=' + self.DS.queryFormat(file.id))
        self.DS.delete(File, 'id=' + self.DS.queryFormat(file.id))
        
    # Don't have access to server memory space, can't independantly verify
    def retrieveMessages(self, tmpdir):
        pass

    # Don't have access to server memory space, so can't test this
    def getStatus(self, tmpdir):
        pass
