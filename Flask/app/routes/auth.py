from flask import Blueprint, request  # blueprint和request都是flask自带的
from extensions import db
from app.models.user import User
from datetime import datetime  # 获取时间戳

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/add")
def add_user_from_web():
    in_username = request.args.get("username")
    in_password = request.args.get("password")

    # 简单拦截
    if not in_username or not in_password:
        return "登记失败：参数不全！"

    # 给其余字段赋值
    new_user = User(
        username=in_username,
        password=in_password,
        nickname="默认昵称",
        role=0,
        real_name="测试姓名",
        avatar_path="/static/default.png",
        create_time=datetime.now(),
    )
    db.session.add(new_user)
    db.session.commit()

    return f"内部录入成功！账号 {in_username} 已完成建档！"
