from extensions import db


class ClassManagement(db.Model):
    __tablename__ = "class_management"
    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    class_name = db.Column(db.String(20), nullable=False)
    class_introduce = db.Column(db.String(50))
    create_time = db.Column(db.DateTime, nullable=False)
