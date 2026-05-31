import datetime
import hmac
import hashlib
import os
from flask import Blueprint, jsonify, request
import jwt
from dotenv import load_dotenv
from app.models import User

auth_bp = Blueprint("auth", __name__)
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-fallback-default-secret-key")


def encrypt_password(raw_password: str) -> str:
    key_bytes = SECRET_KEY.encode("utf-8")
    pwd_bytes = raw_password.encode("utf-8")
    hashed = hmac.new(key_bytes, pwd_bytes, digestmod=hashlib.sha256)
    return hashed.hexdigest()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    in_username = data.get("username")
    in_password = data.get("password")

    if not in_username or not in_password:
        return jsonify(
            {"code": 400, "msg": "❌ 登录拦截：账号和密码不能为空！", "data": None}
        ), 400

    user = User.query.filter_by(username=in_username).first()

    if user is None:
        return jsonify(
            {"code": 404, "msg": "❌ 登录拦截：该账号不存在！", "data": None}
        ), 404

    computed_password = encrypt_password(in_password)

    if user.password != computed_password:
        return jsonify(
            {"code": 401, "msg": "❌ 登录拦截：密码错误，请重新输入！", "data": None}
        ), 401

    payload = {
        "sub": str(user.user_id),
        "role": user.role,
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify(
        {
            "code": 200,
            "msg": f"✅ 登录成功！欢迎回来，{user.nickname}。系统识别您的权限角色为：{user.role_name}。",
            "data": {
                "token": token,
            },
        }
    )
