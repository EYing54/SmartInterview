from datetime import datetime

from app.models.question import TagPool
from app.utils.auth import role_required
from extensions import db
from flask import Blueprint, jsonify, request
from sqlalchemy import func

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
    if TagPool.query.filter(
        func.lower(TagPool.tag_name) == tag_name.lower(), TagPool.is_deleted == 0
    ).first():
        return jsonify({"code": 409, "msg": "标签名称重复！", "data": None}), 409
    new_tag = TagPool(tag_name=tag_name, is_deleted=0, create_time=datetime.now())
    db.session.add(new_tag)
    db.session.commit()
    return jsonify({"code": 200, "msg": "标签添加成功！", "data": None})


@tag_bp.route("/modify_tag_name", methods=["POST"])
@role_required(2)
def modify_tag_name():
    data = request.json or {}
    tag_id = data.get("tag_id", "")
    new_tag_name = data.get("new_tag_name", "").strip()
    if not tag_id or not new_tag_name:
        return jsonify({"code": 400, "msg": "未获取到数据！", "data": None}), 400
    tag_object = TagPool.query.filter_by(is_deleted=0, tag_id=tag_id).first()
    if not tag_object:
        return jsonify({"code": 404, "msg": "未找到相关标签！", "data": None}), 404
    if TagPool.query.filter(
        func.lower(TagPool.tag_name) == new_tag_name.lower(),
        TagPool.is_deleted == 0,
        TagPool.tag_id != tag_object.tag_id,
    ).first():  # 判断修改后的标签是否与已有标签重名
        return jsonify({"code": 409, "msg": "该标签已存在！", "data": None}), 409
    tag_object.tag_name = new_tag_name
    db.session.commit()
    return jsonify({"code": 200, "msg": "标签修改成功！", "data": None})


@tag_bp.route("/delete_tag", methods=["POST"])
@role_required(2)
def delete_tag_name():
    data = request.json or {}
    tag_id = data.get("tag_id", "")
    target_tag_name = data.get("target_tag_name", "").strip()
    if not tag_id or not target_tag_name:
        return jsonify({"code": 400, "msg": "未获取到数据！", "data": None}), 400
    tag_object = TagPool.query.filter_by(
        is_deleted=0, tag_id=tag_id, tag_name=target_tag_name
    ).first()  # 删除标签的时候经行id和name的双重验证
    if not tag_object:
        return jsonify({"code": 404, "msg": "未找到相关标签！", "data": None}), 404
    tag_object.is_deleted = 1
    db.session.commit()
    return jsonify({"code": 200, "msg": "标签删除成功！", "data": None})


@tag_bp.route("/search_tags", methods=["POST"])
@role_required(2)
def query_tag():
    data = request.json or {}
    keyword = data.get("keyword", "").strip()
    if not keyword:
        return jsonify({"code": 400, "msg": "未获取到数据！", "data": None}), 400
    result = TagPool.query.filter(
        TagPool.tag_name.like(f"%{keyword}%"), TagPool.is_deleted == 0
    ).all()  # SQLAlchemy的模糊搜索"like("%name%")"
    if not result:
        return jsonify({"code": 404, "msg": "未查询到结果！", "data": None}), 404
    tags_list = []
    for i in result:
        tags_list.append({"tag_id": i.tag_id, "tag_name": i.tag_name})
    return jsonify({"code": 200, "msg": "查询完成！", "data": tags_list})
