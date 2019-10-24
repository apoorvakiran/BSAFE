import os
from flask import Flask
from flask_cors import CORS
from periodiq import PeriodiqMiddleware
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_dramatiq import DramatiqIntegration
from .extensions import dramatiq
from .api import api

def create_app():
    environment = os.getenv('ENVIRONMENT', 'development')
    if environment != 'development':
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            integrations=[FlaskIntegration(), DramatiqIntegration()],
            environment=environment
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
        logging.FileHandler(f"{app.config['LOG_FOLDER']}/log.log"),
        logging.StreamHandler()
    ])
