from flask import Blueprint, jsonify, request
from app.models import User  # 从models中导入user表

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
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
            )

        elif user.password != in_password:
            return jsonify(
                {
                    "code": 400,
                    "msg": "❌ 登录拦截：密码错误，请重新输入！",
                    "data": None,
                }
            )

        else:
            return jsonify(
                {
                    "code": 200,
                    "msg": f"✅ 登录成功！欢迎回来，{user.real_name}。系统识别您的权限角色为：{user.role}。",
                    "data": None,
                }
            )
