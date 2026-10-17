from extensions import db
from sqlalchemy.dialects.mysql import TINYINT


class JobPosition(db.Model):
    __tablename__ = "job_position"
    job_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_name = db.Column(db.String(30), unique=True, nullable=False)
    is_enabled = db.Column(TINYINT, nullable=False, default=1)
