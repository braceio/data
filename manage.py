
from flask.ext.script import Manager

from main import main_app, settings

manager = Manager(bd_app)

@manager.command
def run(port=5000):
    print "debug is %s" % str(data_app.debug)
    bd_app.run(port=int(port))

if __name__ == "__main__":
    manager.run()
