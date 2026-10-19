from datetime import datetime

from app.models.question import TagPool
from app.utils.auth import role_required
from extensions import db
from flask import Blueprint, jsonify, request

tag_bp = Blueprint("tag", __name__)


@tag_bp.route("/get_tags", methods=["post"])
@role_required(2)
def get_tags():
    tags = TagPool.query.filter_by(is_deleted=0).all()
    tag_list = []
    for i in tags:
        tag_object = {"tag_id": i.tag_id, "tag_name": i.tag_name}
        tag_list.append(tag_object)
    return jsonify({"code": 200, "msg": "标签获取成功！", "data": tag_list})


@tag_bp.route("/add_tag", methods=["POST"])
@role_required(2)
def add_tag():
    data = request.json or {}
    tag_name = data.get("tag_name", "").strip()
    if not tag_name:
        return jsonify({"code": 400, "msg": "未获取到数据！", "data": None}), 400
    if TagPool.query.filter_by(tag_name=tag_name, is_deleted=0).first():
        return jsonify({"code": 409, "msg": "标签名称重复！", "data": None}), 409
    new_tag = TagPool(tag_name=tag_name, is_deleted=0, create_time=datetime.now())
    db.session.add(new_tag)
    db.session.commit()
    return jsonify({"code": 200, "msg": "标签添加成功！", "data": None})
