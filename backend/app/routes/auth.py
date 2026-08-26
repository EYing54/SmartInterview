import os
from datetime import datetime, timedelta, timezone

import jwt
from app.models import User
from app.utils.encrypt import encrypt_password
from dotenv import load_dotenv  # noqa: F401
from flask import Blueprint, jsonify, request

auth_bp = Blueprint("auth", __name__)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY 环境变量未设置！")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    in_username = data.get("username")
    in_password = data.get("password")

    if not in_username or not in_password:
        return jsonify({"code": 400, "msg": "账号和密码不能为空！", "data": None}), 400

    user = User.query.filter_by(username=in_username).first()

    if user is None:
        return jsonify({"code": 404, "msg": "该账号不存在！", "data": None}), 404

    computed_password = encrypt_password(in_password)

    if user.password != computed_password:
        return jsonify(
            {"code": 401, "msg": "密码错误，请重新输入！", "data": None}
        ), 401

    current_time = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.user_id),
        "role": user.role,
        "iat": current_time,
        "exp": current_time + timedelta(hours=1),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify(
        {
            "code": 200,
            "msg": f"登录成功！欢迎回来，{user.nickname}。您的权限角色为：{user.role_name}。",
            "data": {
                "token": token,
                "role": user.role,
            },
        }
    )
