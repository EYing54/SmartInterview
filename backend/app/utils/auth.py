import os
import jwt
from functools import wraps
from flask import request, jsonify, g


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify(
                {"code": 401, "msg": "缺少token，请先登录", "data": None}
            ), 401
        token = auth_header[7:]
        try:
            SECRET_KEY = os.getenv("JWT_SECRET_KEY")
            if not SECRET_KEY:
                raise RuntimeError("JWT_SECRET_KEY 环境变量未设置！")
            decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.current_user_id = decoded_data.get("sub")
            g.current_user_role = decoded_data.get("role")
        except jwt.ExpiredSignatureError:
            return jsonify(
                {"code": 401, "msg": "token已过期，请重新登录", "data": None}
            ), 401
        except jwt.InvalidTokenError:
            return jsonify({"code": 401, "msg": "无效的token", "data": None}), 401
        return f(*args, **kwargs)

    return decorated


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            current_role = g.current_user_role
            if current_role is not None:
                current_role = int(current_role)

            if current_role not in allowed_roles:
                return jsonify(
                    {
                        "code": 403,
                        "msg": "您无权访问此接口",
                        "data": None,
                    }
                ), 403
            return f(*args, **kwargs)

        return decorated

    return decorator
