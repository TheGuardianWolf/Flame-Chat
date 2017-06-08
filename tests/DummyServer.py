from threading import Thread
from app.Server import Server

def dummy():
    server = Server()
    t = Thread(target=server.start)
    t.daemon = True
    t.start()
    return t

def main():
    dummy()

if __name__ == '__main__':
    main()
