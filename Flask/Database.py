from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import TINYINT

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:313708@localhost:3306/smart_interview_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(TINYINT, nullable=False)


class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    nickname = db.Column(db.String(20), nullable=False)
    real_name = db.Column(db.String(30), nullable=False)
    avatar_path = db.Column(db.String(255), nullable=False)


class Teacher(db.Model):
    __tablename__ = "teacher"
    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    real_name = db.Column(db.String(30), nullable=False)
    avatar_path = db.Column(db.String(255), nullable=False)


class Admin(db.Model):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    permission = db.Column(TINYINT, nullable=False)


class ClassInfo(db.Model):
    __tablename__ = "class"
    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_name = db.Column(db.String(20), nullable=False)
    class_introduce = db.Column(db.String(50))
    invitation_code = db.Column(db.String(6), nullable=False)


class InterviewRecord(db.Model):
    __tablename__ = "interview_record"
    interview_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    )
    create_time = db.Column(db.Date, nullable=False)
    dimension_grade_1 = db.Column(db.Numeric(5, 2))
    dimension_grade_2 = db.Column(db.Numeric(5, 2))
    dimension_grade_3 = db.Column(db.Numeric(5, 2))
    dimension_grade_4 = db.Column(db.Numeric(5, 2))
    dimension_grade_5 = db.Column(db.Numeric(5, 2))
    video_path = db.Column(db.String(255))
    audio_path = db.Column(db.String(255))
    analysis_text = db.Column(db.Text)
    teacher_comment = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.teacher_id"))
    comment_time = db.Column(db.DateTime)
    status = db.Column(TINYINT, nullable=False)


class ResumeRecord(db.Model):
    __tablename__ = "resume_record"
    resume_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    )
    create_time = db.Column(db.Date, nullable=False)
    dimension_grade_1 = db.Column(db.Numeric(5, 2))
    dimension_grade_2 = db.Column(db.Numeric(5, 2))
    dimension_grade_3 = db.Column(db.Numeric(5, 2))
    dimension_grade_4 = db.Column(db.Numeric(5, 2))
    dimension_grade_5 = db.Column(db.Numeric(5, 2))
    file_path = db.Column(db.String(255))
    analysis_text = db.Column(db.Text)
    teacher_comment = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.teacher_id"))
    comment_time = db.Column(db.DateTime)
    status = db.Column(TINYINT, nullable=False)


class QuestionBank(db.Model):
    __tablename__ = "question_bank"
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)


class TagPool(db.Model):
    __tablename__ = "tag_pool"
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(20), nullable=False)


class QuestionTagRelation(db.Model):
    __tablename__ = "question_tag_relation"
    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(
        db.Integer, db.ForeignKey("question_bank.question_id"), nullable=False
    )
    tag_id = db.Column(db.Integer, db.ForeignKey("tag_pool.tag_id"), nullable=False)


class InterviewQuestionRelation(db.Model):
    __tablename__ = "interview_question_relation"
    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    interview_id = db.Column(
        db.Integer, db.ForeignKey("interview_record.interview_id"), nullable=False
    )
    question_id = db.Column(
        db.Integer, db.ForeignKey("question_bank.question_id"), nullable=False
    )
    question_order = db.Column(db.Integer, nullable=False)


class StudentClassRelation(db.Model):
    __tablename__ = "student_class_relation"
    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    )
    class_id = db.Column(db.Integer, db.ForeignKey("class.class_id"), nullable=False)


class TeacherClassRelation(db.Model):
    __tablename__ = "teacher_class_relation"
    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teacher.teacher_id"), nullable=False
    )
    class_id = db.Column(db.Integer, db.ForeignKey("class.class_id"), nullable=False)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Successful Create!")
