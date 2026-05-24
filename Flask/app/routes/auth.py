from flask import Blueprint, jsonify, request
from app.models import User  # 从models中导入user表

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # HTML 登录页面用于测试
    if request.method == "GET":
        return """
            <div style="margin: 50px;">
                <h2>智能面试系统 - 门禁测试</h2>
                <form method="POST">
                    账号: <input type="text" name="username"><br><br>
                    密码: <input type="password" name="password"><br><br>
                    <input type="submit" value="验证身份">
                </form>
            </div>
        """

    # 输入账号密码并点击“验证身份”按钮时（POST请求）
    if request.method == "POST":
        # 拦截前端表单传过来的账号和密码
        in_username = request.form.get("username")
        in_password = request.form.get("password")

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
