from app.Services.DatabaseService import DatabaseService
from app.Models.AuthModel import Auth
from os import path

class TestDatabaseService(object):
    def __setup(self, tmpdir):
        self.DS = DatabaseService(path.join(str(tmpdir), 'entity.db'))
    
    def test_insertMany(self, tmpdir):
        self.__setup(tmpdir)
        models = [
            Auth(None, 'testUser1', 'testPassword1'),
            Auth(None, 'testUser2', 'testPassword2')
        ]
        ids = self.DS.insertMany(models)
        selected = self.DS.query('SELECT * FROM auth', fetch=True)
        for i, model in enumerate(models):
            dbEntry = selected[i]
            assert ids[i] == dbEntry[0]
            assert model.username == dbEntry[1]
            assert model.passhash == dbEntry[2]

    def test_insert(self, tmpdir):
        self.__setup(tmpdir)
        model = Auth(None, 'user', 'hash')
        id = self.DS.insert(model)
        dbEntry = self.DS.query('SELECT * FROM auth', fetch=True)[0]
        assert id == dbEntry[0]
        assert model.username == dbEntry[1]
        assert model.passhash == dbEntry[2]