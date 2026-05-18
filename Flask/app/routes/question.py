from flask import Blueprint, request  # noqa: F401
from app.models.question import QuestionBank
from extensions import db
from datetime import datetime

question_bp = Blueprint("question", __name__)


@question_bp.route("/query_question")
def query_question():
    questions = QuestionBank.query.all()
    return str(questions)


@question_bp.route("/add_question")
def add_question():
    new_question = QuestionBank(
        question="请说明TCP和UDP的区别",
        answer="TCP面向连接且可靠；UDP无连接，不保证可靠交付。",
        is_deleted=0,
        create_time=datetime.now(),
    )
    db.session.add(new_question)
    db.session.commit()
    return "新增成功！"
