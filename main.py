from sys import argv

from app import Application

if __name__ == '__main__':
    app = Application()
    app.run(*argv[1:])
