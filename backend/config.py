import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 从.env获取账号和密码
db_user = os.getenv("DB_USER")
db_pwd = os.getenv("DB_PASSWORD")
db_na = os.getenv("DB_NAME")

# 最终的连接
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_pwd}@127.0.0.1:3306/{db_na}"

# 从环境变量读取音视频存储路径
INTERVIEW_MEDIA_DIR = os.environ.get("INTERVIEW_MEDIA_DIR")
