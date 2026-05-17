from extensions import db
from sqlalchemy.dialects.mysql import TINYINT


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    nickname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(TINYINT, nullable=False)
    real_name = db.Column(db.String(30), nullable=False)
    avatar_path = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("class_management.class_id"))
