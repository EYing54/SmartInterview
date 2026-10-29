from datetime import datetime

from app.models.question import QuestionBank, QuestionTagRelation, TagPool
from app.utils.auth import role_required
from extensions import db
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

question_bp = Blueprint("question", __name__)


# 获取已有题目
@question_bp.route("/get_questions", methods=["POST"])
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


# 添加新的题目
@question_bp.route("/add_questions", methods=["POST"])
@role_required(2)
def add_question():
    data = request.json or {}
    if not data:
        return jsonify({"code": 400, "msg": "未获取到数据！", "data": None}), 400
    # 对question和answer都进行字符串的判断
    question = data.get("question", "")
    answer = data.get("answer", "")
    if not isinstance(question, str) or not isinstance(answer, str):
        return jsonify(
            {"code": 400, "msg": "题目和答案必须是字符串！", "data": None}
        ), 400
    question = question.strip()
    answer = answer.strip()
    question_tags = data.get("tag_ids", [])
    # 对question_tags进行数据类型的判断，排除非list以及int类型的数据
    if not isinstance(question_tags, list):  # 判断question_tags的数据类型是否为list
        return jsonify({"code": 400, "msg": "标签数据必须是列表！", "data": None}), 400
    if len(question_tags) == 0:
        return jsonify({"code": 400, "msg": "请至少选择一个标签！", "data": None}), 400
    for i in question_tags:
        if not isinstance(i, int) or isinstance(i, bool):  # bool值也属于int类型
            return jsonify(
                {"code": 400, "msg": "标签数据类型错误！", "data": None}
            ), 400
    if not question or not answer or not question_tags:
        return jsonify({"code": 400, "msg": "缺少必需数据！", "data": None}), 400
    # 对复杂的数据操作进行异常处理
    try:
        new_question = QuestionBank(
            question=question, answer=answer, create_time=datetime.now()
        )
        db.session.add(new_question)
        db.session.flush()  # 把待处理操作,即add(new_question)发送到数据库，但不提交事务。
        question_id = new_question.question_id
        for i in set(question_tags):
            if not TagPool.query.filter_by(tag_id=i, is_deleted=0).first():
                db.session.rollback()  # 若遇到数据库没有标签id则进行事务回滚，撤回add()
                return jsonify(
                    {"code": 404, "msg": "未找到相关标签！", "data": None}
                ), 404  # 拦截数据库没有的标签
            new_relation = QuestionTagRelation(
                tag_id=i, question_id=question_id, create_time=datetime.now()
            )
            db.session.add(new_relation)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()  # 出现异常后进行回滚
        return jsonify({"code": 500, "msg": "数据库操作失败！", "data": None}), 500

    return jsonify({"code": 200, "msg": "题目添加成功！", "data": None})


# 删除题目
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
