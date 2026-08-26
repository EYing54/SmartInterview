import hashlib
import hmac
import os

from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def encrypt_password(raw_password: str) -> str:  # 以字符串输入原始密码
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY 环境变量未设置！")

    key_bytes = SECRET_KEY.encode("utf-8")  # 额外增加的密钥“JWT”
    pwd_bytes = raw_password.encode("utf-8")  # 原始的密码
    hashed = hmac.new(key_bytes, pwd_bytes, digestmod=hashlib.sha256)
    return hashed.hexdigest()
