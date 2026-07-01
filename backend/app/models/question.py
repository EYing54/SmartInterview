from extensions import db
from sqlalchemy.dialects.mysql import TINYINT


# 题库
class QuestionBank(db.Model):
    __tablename__ = "question_bank"
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(TINYINT, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)


# 标签池
class TagPool(db.Model):
    __tablename__ = "tag_pool"
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(20), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)


# 题目标签关联表
class QuestionTagRelation(db.Model):
    __tablename__ = "question_tag_relation"
    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(
        db.Integer, db.ForeignKey("question_bank.question_id"), nullable=False
    )
    tag_id = db.Column(db.Integer, db.ForeignKey("tag_pool.tag_id"), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)
