from flask import Flask
from flask_cors import CORS
from periodiq import PeriodiqMiddleware

from .extensions import dramatiq
from .api import api

def create_app():
    app = Flask(__name__)

    # Beware that app config must be loaded before you initialize Dramatiq
    # extension with app.
    app.config.from_pyfile('config.py', silent=True)
    dramatiq.middleware.append(PeriodiqMiddleware())
    dramatiq.init_app(app)

    app.register_blueprint(api)
    CORS(app)
    return app
