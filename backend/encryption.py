import hmac
import hashlib
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


# 🚨 这里的密钥必须和你的 .env 文件中的 JWT_SECRET_KEY 完全一致！
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
raw_password = "2460105133"

# 运算生成密文
hashed = hmac.new(
    SECRET_KEY.encode("utf-8"), raw_password.encode("utf-8"), digestmod=hashlib.sha256
)
print(hashed.hexdigest())
# 会输出类似：85e4b7...（一串64位的固定字符串，把它存进数据库即可）
