import datetime
import os

from app.models.user import User
from app.utils.auth import role_required
from app.utils.encrypt import encrypt_password
from extensions import db
from flask import Blueprint, current_app, g, jsonify, request, send_from_directory

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/get_user_profile", methods=["POST"])
@role_required(0, 1, 2)
def get_user_profile():
    current_user_id = g.current_user_id
    user_info = User.query.filter_by(user_id=current_user_id).first()
    if not user_info:
        return jsonify({"code": 404, "msg": "用户不存在！", "data": None}), 404
    target_info = {
        "username": user_info.username,
        "nickname": user_info.nickname,
        "real_name": user_info.real_name,
        "post": user_info.post,
        "avatar_path": user_info.avatar_path,
    }
    return jsonify({"code": 200, "msg": "获取用户信息成功！", "data": target_info})


@profile_bp.route("/upload_avatar", methods=["POST"])
@role_required(0, 1, 2)
def upload_avatar():
    current_user_id = g.current_user_id
    user = User.query.filter_by(user_id=current_user_id).first()
    if not user:
        return jsonify({"code": 404, "msg": "未找到用户！", "data": None}), 404
    avatar = request.files.get("avatar")
    if not avatar:
        return jsonify({"code": 400, "msg": "未获取到图片！", "data": None}), 400
    filename = avatar.filename
    filename_split = os.path.splitext(filename)
    filename_extension = str(filename_split[1]).lower()
    safety_extensions = [".png", ".jpg", ".jpeg", ".webp"]
    num = 0
    for i in safety_extensions:
        if i != filename_extension:
            num = num + 1
        elif i == filename_extension:
            break
        if num == 4:
            return jsonify({"code": 400, "msg": "图片格式错误！", "data": None}), 400
    time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    modified_filename = f"{current_user_id}_{time}{filename_extension}"
    avatar_dir = current_app.config.get("AVATAR_MEDIA_DIR")
    if not avatar_dir:
        return jsonify({"code": 500, "msg": "服务器配置错误！", "data": None}), 500
    user_avatar_dir = os.path.join(avatar_dir, f"user_{current_user_id}")
    os.makedirs(user_avatar_dir, exist_ok=True)
    avatar_save_path = os.path.join(user_avatar_dir, modified_filename)
    avatar.save(avatar_save_path)
    user.avatar_path = modified_filename
    db.session.commit()
    return jsonify({"code": 200, "msg": "头像已储存！", "data": None})


@profile_bp.route("/get_user_avatar/<filename>", methods=["GET"])
@role_required(0, 1, 2)
def get_user_avatar(filename):
    current_user_id = g.current_user_id
    avatar_dir = current_app.config.get("AVATAR_MEDIA_DIR")
    if not avatar_dir:
        return jsonify({"code": 500, "msg": "服务器配置错误！", "data": None}), 500
    user_avatar_dir = os.path.join(avatar_dir, f"user_{current_user_id}")
    full_path = os.path.join(user_avatar_dir, filename)
    if not os.path.exists(full_path):
        return jsonify({"code": 404, "msg": "头像文件不存在！", "data": None}), 404
    return send_from_directory(user_avatar_dir, filename)


@profile_bp.route("/modify_post", methods=["POST"])
@role_required(0)
def modify_post():
    data = request.json or {}
    raw_data = data.get("new_post", "")
    new_post = str(raw_data).strip()
    if not new_post:
        return jsonify({"code": 400, "msg": "未获取到数据！", "data": None}), 400
    if len(new_post) > 30:
        return jsonify({"code": 400, "msg": "字符串长度过长！", "data": None}), 400
    current_user_id = g.current_user_id
    user_info = User.query.filter_by(user_id=current_user_id).first()
    if not user_info:
        return jsonify({"code": 404, "msg": "未找到用户！", "data": None}), 404
    user_info.post = str(new_post)
    db.session.commit()
    return jsonify({"code": 200, "msg": "意向岗位修改成功！", "data": None})


@profile_bp.route("/modify_nickname", methods=["POST"])
@role_required(0, 1, 2)
def modify_nickname():
    data = request.json or {}
    raw_data = data.get("new_nickname", "")
    new_nickname = str(raw_data).strip()
    if not new_nickname:
        return jsonify({"code": 400, "msg": "未获取到数据！", "data": None}), 400
    if len(new_nickname) > 20:
        return jsonify({"code": 400, "msg": "字符串长度过长！", "data": None}), 400
    current_user_id = g.current_user_id
    user_info = User.query.filter_by(user_id=current_user_id).first()
    if not user_info:
        return jsonify({"code": 404, "msg": "未找到用户！", "data": None}), 404
    if new_nickname == user_info.nickname:
        return jsonify({"code": 422, "msg": "新昵称与旧昵称相同！", "data": None}), 422
    user_info.nickname = new_nickname
    db.session.commit()
    return jsonify({"code": 200, "msg": "昵称修改成功！", "data": None})


@profile_bp.route("/modify_password", methods=["POST"])
@role_required(0, 1, 2)
def modify_password():
    data = request.json or {}
    raw_data_old_password = data.get("old_password", "")
    old_password = str(raw_data_old_password).strip()
    raw_data_new_password = data.get("new_password", "")
    new_password = str(raw_data_new_password).strip()
    if not old_password or not new_password:
        return jsonify({"code": 400, "msg": "未获取到数据！", "data": None}), 400
    if len(old_password) > 50 or len(new_password) > 50:
        return jsonify({"code": 400, "msg": "字符串长度过长！", "data": None}), 400
    if old_password == new_password:
        return jsonify({"code": 422, "msg": "新密码与原密码相同！", "data": None}), 422
    current_user_id = g.current_user_id
    user_info = User.query.filter_by(user_id=current_user_id).first()
    if not user_info:
        return jsonify({"code": 404, "msg": "未找到用户！", "data": None}), 404
    original_password = user_info.password
    encryptional_password = encrypt_password(old_password)
    if encryptional_password != original_password:
        return jsonify({"code": 400, "msg": "旧密码输入错误！", "data": None}), 400
    user_info.password = encrypt_password(new_password)
    db.session.commit()
    return jsonify({"code": 200, "msg": "密码修改成功！", "data": None})
