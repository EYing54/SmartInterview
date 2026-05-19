from flask import Blueprint, request, jsonify  # noqa: F401
from app.models.question import QuestionBank
from extensions import db
from datetime import datetime

question_bp = Blueprint("question", __name__)


@question_bp.route("/query_question")
def query_question():
    questions = QuestionBank.query.all()
    result_list = []
    for i in questions:
        i_dict = {
            "question_id": i.question_id,
            "question": i.question,
            "answer": i.answer,
            "is_deleted": i.is_deleted,
            "create_time": i.create_time,
        }
        result_list.append(i_dict)
    return jsonify({"code": 200, "msg": "题目查询成功！", "data": result_list})


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
