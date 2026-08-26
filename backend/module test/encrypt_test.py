import hashlib
import hmac
import os

from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
raw_password = "sjiwug@Ds^&584@*aw1&"

# 运算生成密文
hashed = hmac.new(
    SECRET_KEY.encode("utf-8"), raw_password.encode("utf-8"), digestmod=hashlib.sha256
)
print(hashed.hexdigest())
