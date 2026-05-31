from extensions import db
from sqlalchemy.dialects.mysql import TINYINT


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    nickname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(TINYINT, nullable=False)
    real_name = db.Column(db.String(30), nullable=False)
    avatar_path = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("class_management.class_id"))
    ROLE_MAP = {0: "学生", 1: "教师", 2: "管理员"}

    @property
    def role_name(self) -> str:
        """动态将数字 role 转换为中文字符串"""
        # 使用 .get() 并在找不到时返回 "未知角色"，防止脏数据导致系统崩溃
        return self.ROLE_MAP.get(self.role, "未知角色")
