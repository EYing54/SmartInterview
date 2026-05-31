from functools import wraps
from flask import jsonify, request


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not token:
            return jsonify(
                {"code": 401, "msg": "缺少token，请先登录", "data": None}
            ), 401
