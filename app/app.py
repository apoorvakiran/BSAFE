from flask import Flask
from flask_cors import CORS
from periodiq import PeriodiqMiddleware
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from .extensions import dramatiq
from .api import api

def create_app():
    sentry_sdk.init(
        dsn="https://4ca7cdcc54274295af09b1f2d98f4960@sentry.io/1728777",
        integrations=[FlaskIntegration()]
    )
    app = Flask(__name__)

    # Beware that app config must be loaded before you initialize Dramatiq
    # extension with app.
    app.config.from_pyfile('config.py', silent=True)
    dramatiq.middleware.append(PeriodiqMiddleware())
    dramatiq.init_app(app)

    app.register_blueprint(api)
    CORS(app)
    configure_logging(app)
    return app

def configure_logging(app):
    import logging
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(app.config['LOG_FOLDER'], 'log')),
        logging.StreamHandler()
    ])
