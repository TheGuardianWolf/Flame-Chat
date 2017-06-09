from app.Services.DatabaseService import DatabaseService
from app.Services.LoginService import LoginService
from app.Services.SecureService import SecureService
from app.Services.RequestService import RequestService
from app.Services.MemoryService import MemoryService
from app.Controllers.PublicController import PublicController
from app import Globals
from os import path

def factory(tmpdir=None):
    if tmpdir is not None:
        return {
            'DatabaseService': DatabaseService(path.join(str(tmpdir), 'entity.db')),
            'LoginService': LoginService(),
            'SecureService': SecureService(path.join(str(tmpdir), 'key'), path.join(str(tmpdir), 'key.pub')),
            'RequestService': RequestService(),
            'MemoryService': MemoryService()
        }
    else:
        return {
            'DatabaseService': DatabaseService(Globals.dbPath),
            'LoginService': LoginService(),
            'SecureService': SecureService(Globals.publicKeyPath, Globals.privateKeyPath),
            'RequestService': RequestService(),
            'MemoryService': MemoryService()
        }