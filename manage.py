
from flask.ext.script import Manager

from main import main_app, settings

manager = Manager(main_app)

@manager.command
def run(port=5000):
    print "debug is %s" % str(main_app.debug)
    main_app.run(port=int(port))

if __name__ == "__main__":
    manager.run()
