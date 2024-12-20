from flask import Flask
from app.services import start_scheduler

def create_app():
    app = Flask(__name__)
    start_scheduler()
    from .routes import main
    app.register_blueprint(main)
    return app
