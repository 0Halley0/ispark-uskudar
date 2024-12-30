from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
from app.services import start_scheduler

# db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    # db.init_app(app)
    from .routes import main
    app.register_blueprint(main)
    start_scheduler()
    return app
