"""This module is the core of the project."""

# Import flask and template operators
from flask import Flask

from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail

from app.exception_handler import init_error_handler
from app.custom.mongodb import MongoAlchemy
from app.hooks import init_hooks
from app.custom.logger import init_logger
from app.custom.flask_redis import Redis
from app.custom.seed import init_seed_script
from app.utils.response_helper import success_response as success, \
                                      failure_response as failure, \
                                      error_response as error
from celery_app.celery_utils import init_celery


# Globally accessible libraries
db = SQLAlchemy()
ma = Marshmallow()
mongodb = MongoAlchemy()
mailer = Mail()
redis = Redis()
socketIo = SocketIO(cors_allowed_origins="*")


def create_app(**kwargs):
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('../config.py')

    db.init_app(app)
    mongodb.init_app(app)
    ma.init_app(app)
    mailer.init_app(app)
    redis.init_app(app)
    socketIo.init_app(app, message_queue=app.config.get("REDIS_URL"))

    # to accept requests when running both
    # the frontend and backend on same server
    CORS(app)

    init_logger(app)
    init_error_handler(app)
    init_hooks(app, app.config['HOOKS_REQUIRED'])

    # Only initialise celery, when it has been called from the run.py.
    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"), app)

    with app.app_context():
        # Import a module/component using its blueprint handler variable (auth)
        from app.auth.controllers import mod_auth as auth_module
        from app.product.controllers import mod_product as product_module
        from app.socket.controllers import mod_socket as socket_module
        from app.socket import socket

        # Register blueprint(s)
        app.register_blueprint(auth_module)
        app.register_blueprint(product_module)
        app.register_blueprint(socket_module)

        init_seed_script()
        return app
