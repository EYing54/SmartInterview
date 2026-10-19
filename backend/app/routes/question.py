from datetime import datetime

from app.models.question import QuestionBank
from app.utils.auth import role_required
from extensions import db
from flask import Blueprint, jsonify, request

question_bp = Blueprint("question", __name__)


@question_bp.route("/get_questions", methods=["POST"])  # 查询题目
@role_required(2)
def get_questions():
    data = request.json or {}
    page = data.get("page", 1)
    size = data.get("size", 20)
    pagination = QuestionBank.query.filter_by(is_deleted=0).paginate(
        page=page, per_page=size, error_out=False
    )
    questions = pagination.items  # 查询数据库中的所有题目
    result_list = []
    for i in questions:
        i_dict = {
            "question_id": i.question_id,
            "question": i.question,
            "answer": i.answer,
            "is_deleted": i.is_deleted,
            "create_time": i.create_time,
        }
        result_list.append(i_dict)  # 将循环中的每一次查到题目的添加到列表中
    return jsonify(
        {
            "code": 200,
            "msg": "题目查询成功！",
            "data": {"total": pagination.total, "list": result_list},
        }
    )  # 返回json数据至前端


@question_bp.route("/delete_question", methods=["POST"])
@role_required(2)
def delete_question():
    data = request.json
    target_id = data.get("question_id")  # 获取前端想要查询的题目id
    if not target_id:  # id判空
        return jsonify({"code": 400, "msg": "请求失败，缺少题目id", "data": None}), 400
    # id数据类型判断
    if not isinstance(target_id, int):
        return jsonify(
            {"code": 400, "msg": "参数类型错误，ID 必须是整数", "data": None}
        )
    target_question = QuestionBank.query.filter_by(question_id=target_id).first()
    if not target_question:  # 题目判空
        return jsonify({"code": 404, "msg": "题目不存在", "data": None}), 404
    target_question.is_deleted = 1  # 修改逻辑删除值
    db.session.commit()  # 提交到数据库
    return jsonify({"code": 200, "msg": "删除成功", "data": None})
