import os

from flask import Flask
from flask_socketio import SocketIO

from proj312.database import Database
from . import database

socketio = SocketIO()
db: Database = None
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs("proj312/static")
    except OSError:
        pass

    global db
    db = database.Database()

    from . import friends
    app.register_blueprint(friends.bp)

    from . import homepage
    app.register_blueprint(homepage.bp)

    from . import log
    app.register_blueprint(log.bp)

    socketio.init_app(app)
    return app
