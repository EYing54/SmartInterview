from app.models.class_management import ClassManagement
from app.models.user import User
from app.utils.auth import role_required
from app.utils.encrypt import encrypt_password
from extensions import db
from flask import Blueprint, jsonify, request

account_bp = Blueprint("user", __name__)


@account_bp.route("/get_student_list", methods=["POST"])
@role_required(2)
def get_student_list():
    data = request.json or {}
    page = data.get("page", 1)
    size = data.get("size", 20)
    pagination = (
        db.session.query(
            User.user_id,
            User.username,
            User.nickname,
            User.real_name,
            ClassManagement.class_name,
        )
        .filter_by(role=0, is_deleted=0)
        .outerjoin(ClassManagement, ClassManagement.class_id == User.class_id)
        .paginate(page=page, per_page=size, error_out=False)
    )
    students = pagination.items
    result_list = []
    for i in students:
        i_dict = {
            "user_id": i.user_id,
            "username": i.username,
            "nickname": i.nickname,
            "real_name": i.real_name,
            "class_name": i.class_name or "暂无班级",
        }
        result_list.append(i_dict)
    return jsonify(
        {
            "code": 200,
            "msg": "学生查询成功！",
            "data": {"total": pagination.total, "list": result_list},
        }
    )


@account_bp.route("/delete_s_account", methods=["POST"])
@role_required(2)
def delete_student():
    data = request.json or {}
    target_users_id = data.get("user_id")
    if not target_users_id or not isinstance(target_users_id, list):
        return jsonify(
            {"code": 400, "msg": "参数错误：user_id 必须是一个非空数组", "data": None}
        ), 400
    affected_rows = User.query.filter(
        User.role == 0, User.user_id.in_(target_users_id)
    ).update({"is_deleted": 1})
    if affected_rows == 0:
        db.session.rollback()
        return jsonify({"code": 404, "msg": "未找到匹配的账号，可能已被删除"}), 404
    db.session.commit()
    return jsonify(
        {"code": 200, "msg": f"成功删除{affected_rows}个账号！", "data": None}
    )


@account_bp.route("/reset_s_account_password", methods=["POST"])
@role_required(2)
def reset_s_password():
    data = request.json or {}
    target_users_id = data.get("user_id")
    if not target_users_id or not isinstance(target_users_id, list):
        return jsonify({"code": 400, "msg": "未获取到有效的id！", "data": None}, 400)
    default_password = encrypt_password("123456789")
    affected_rows = User.query.filter(User.user_id.in_(target_users_id)).update(
        {"password": default_password}
    )
    if affected_rows == 0:
        db.session.rollback()
        return jsonify({"code": 404, "msg": "未找到匹配的账号！"}), 404
    db.session.commit()
    return jsonify(
        {"code": 200, "msg": f"成功重置{affected_rows}个账号的密码", "data": None}
    )


@account_bp.route("/get_teacher_list", methods=["POST"])
@role_required(2)
def get_teacher_list():
    data = request.json or {}
    page = data.get("page", 1)
    size = data.get("size", 20)
    pagination = (
        db.session.query(
            User.user_id,
            User.username,
            User.nickname,
            User.real_name,
        )
        .filter_by(role=1, is_deleted=0)
        .paginate(page=page, per_page=size, error_out=False)
    )
    teachers = pagination.items
    result_list = []
    for i in teachers:
        i_dict = {
            "user_id": i.user_id,
            "username": i.username,
            "nickname": i.nickname,
            "real_name": i.real_name,
        }
        result_list.append(i_dict)
    return jsonify(
        {
            "code": 200,
            "msg": "教师查询成功！",
            "data": {"total": pagination.total, "list": result_list},
        }
    )


@account_bp.route("/delete_t_account")
@role_required(2)
def delete_t_account():
    data = request.json() or {}
    target_users_id = data.get("user_id")
    if not target_users_id or not isinstance(target_users_id, list):
        return jsonify(
            {"code": 400, "msg": "参数错误：user_id 必须是一个非空数组", "data": None}
        ), 400
    affected_rows = User.query.filter(
        User.role == 1, User.user_id.in_(target_users_id)
    ).update({"is_deleted": 1})
    if affected_rows == 0:
        db.session.rollback()
        return jsonify({"code": 404, "msg": "未找到匹配的账号，可能已被删除"}), 404
    db.session.commit()
    return jsonify(
        {"code": 200, "msg": f"成功删除{affected_rows}个账号！", "data": None}
    )


@account_bp.route("/reset_t_account_password", methods=["POST"])
@role_required(2)
def reset_t_password():
    data = request.json or {}
    target_users_id = data.get("user_id")
    if not target_users_id or not isinstance(target_users_id, list):
        return jsonify({"code": 400, "msg": "未获取到有效的id！", "data": None}, 400)
    default_password = encrypt_password("123456789")
    affected_rows = User.query.filter(User.user_id.in_(target_users_id)).update(
        {"password": default_password}
    )
    if affected_rows == 0:
        db.session.rollback()
        return jsonify({"code": 404, "msg": "未找到匹配的账号！"}), 404
    db.session.commit()
    return jsonify(
        {"code": 200, "msg": f"成功重置{affected_rows}个账号的密码", "data": None}
    )
