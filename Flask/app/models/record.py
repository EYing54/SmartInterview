from extensions import db
from sqlalchemy.dialects.mysql import TINYINT


class InterviewRecord(db.Model):
    __tablename__ = "interview_record"
    interview_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    question_record = db.Column(db.JSON, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)
    dimension_grade = db.Column(db.Numeric(5, 2))
    video_path = db.Column(db.String(255))
    audio_path = db.Column(db.String(255))
    analysis_text = db.Column(db.Text)
    teacher_comment = db.Column(db.Text)
    comment_time = db.Column(db.DateTime)
    post = db.Column(db.String(30), nullable=False)
    status = db.Column(TINYINT, nullable=False, default=0)

    # User作为不同属性的外键需要多一个“指路”的步骤
    student = db.relationship("User", foreign_keys=[student_id])
    teacher = db.relationship("User", foreign_keys=[teacher_id])


class ResumeRecord(db.Model):
    __tablename__ = "resume_record"
    resume_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    create_time = db.Column(db.DateTime, nullable=False)
    dimension_grade = db.Column(db.JSON)
    file_path = db.Column(db.String(255))
    analysis_text = db.Column(db.Text)
    teacher_comment = db.Column(db.Text)
    comment_time = db.Column(db.DateTime)
    post = db.Column(db.String(30), nullable=False)
    status = db.Column(TINYINT, nullable=False, default=0)

    # 路线指引（同上）
    student = db.relationship("User", foreign_keys=[student_id])
    teacher = db.relationship("User", foreign_keys=[teacher_id])
