from datetime import datetime

from app.models.question import QuestionBank, QuestionTagRelation, TagPool
from app.utils.auth import role_required
from extensions import db
from flask import Blueprint, jsonify, request
from sqlalchemy import func
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
    question_ids = [i.question_id for i in questions]  # 列表推导式，返回的是一个列表
    tags = (
        db.session.query(QuestionTagRelation.question_id, TagPool.tag_name)
        .join(TagPool, TagPool.tag_id == QuestionTagRelation.tag_id)
        .filter(QuestionTagRelation.question_id.in_(question_ids))
        .all()
    )
    tag_map = {}
    for i in tags:
        # 某个键不存在时，自动创建一个默认值，同时也会返回这个默认值（可以直接调用append）
        tag_map.setdefault(i.question_id, []).append(i.tag_name)
    result_list = []
    for i in questions:
        i_dict = {
            "question_id": i.question_id,
            "question": i.question,
            "answer": i.answer,
            "create_time": i.create_time,
            "question_tags": tag_map.get(i.question_id, []),
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
        existing_question = QuestionBank.query.filter(
            func.lower(QuestionBank.question) == question.lower(),
            QuestionBank.is_deleted == 0,
        ).first()
        if existing_question:
            return jsonify({"code": 409, "msg": "该题目已存在！", "data": None}), 409
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
    target_ids = data.get("question_ids")  # 获取前端想要查删除的题目的id

    # id列表的数据类型判断
    if not isinstance(target_ids, list):
        return jsonify(
            {"code": 400, "msg": "参数类型错误，必须是列表", "data": None}
        ), 400
    if not target_ids:  # id_list判空
        return jsonify({"code": 400, "msg": "请求失败，缺少题目id", "data": None}), 400
    if not all(
        type(question_id) is int and question_id > 0 for question_id in target_ids
    ):
        return jsonify({"code": 400, "msg": "题目ID必须是正整数！", "data": None}), 400
    target_ids = list(set(target_ids))  # 去重
    update_count = QuestionBank.query.filter(
        QuestionBank.is_deleted == 0, QuestionBank.question_id.in_(target_ids)
    ).update(
        {QuestionBank.is_deleted: 1}, synchronize_session=False
    )  # 用update()批量更新数据，返回的值是更新数据的数量
    if update_count == 0:  # 题目判空
        return jsonify({"code": 404, "msg": "题目不存在", "data": None}), 404
    if update_count != len(target_ids):
        db.session.rollback()
        return jsonify(
            {"code": 404, "msg": "部分题目不存在或已经删除！", "data": None}
        ), 404
    db.session.commit()  # 提交到数据库
    return jsonify({"code": 200, "msg": "删除成功", "data": None})
