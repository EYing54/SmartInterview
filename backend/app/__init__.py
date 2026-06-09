from flask import Flask
from flask_cors import CORS
from extensions import db, scheduler
from app.routes.auth import auth_bp
from app.routes.question import question_bp
from app.routes.interview import interview_bp


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object("config")

    db.init_app(app)

    app.config["SCHEDULER_API_ENABLED"] = True
    scheduler.init_app(app)
    scheduler.app = app

    from app.utils import tasks  # noqa: F401

    scheduler.start()

    app.register_blueprint(auth_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(interview_bp)

    return app
