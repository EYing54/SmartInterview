from flask import Blueprint, jsonify, request
import jwt
from app.models import User  # 从models中导入user表
import datetime
from dotenv import load_dotenv
import os

auth_bp = Blueprint("auth", __name__)
load_dotenv()


@auth_bp.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        # 拦截前端表单传过来的账号和密码
        data = request.json
        in_username = data.get("username")
        in_password = data.get("password")

        # 对比数据库中的数据
        user = User.query.filter_by(username=in_username).first()

        # 身份核验
        if user is None:
            return jsonify(
                {"code": 404, "msg": "❌ 登录拦截：该账号不存在！", "data": None}
            ), 404

        elif user.password != in_password:
            return jsonify(
                {
                    "code": 401,
                    "msg": "❌ 登录拦截：密码错误，请重新输入！",
                    "data": None,
                }
            ), 401

        else:
            payload = {
                "user": user.user_id,
                "role": user.role,
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=2),
            }
            SECRET_KEY = os.getenv("JWT_SECRET_KEY")
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return jsonify(
                {
                    "code": 200,
                    "msg": f"✅ 登录成功！欢迎回来，{user.nickname}。系统识别您的权限角色为：{user.role}。",
                    "data": {"token": token},
                }
            )
