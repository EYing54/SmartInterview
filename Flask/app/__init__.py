from flask import Flask
from extensions import db
from app.routes.auth import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    db.init_app(app)
    app.register_blueprint(auth_bp)

    return app
