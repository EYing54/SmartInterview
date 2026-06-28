from app.models.class_management import ClassManagement
from app.models.record import InterviewRecord, ResumeRecord
from app.models.user import User
from extensions import db
from flask import Blueprint, jsonify, g, request
from app.utils.auth import role_required
from datetime import datetime

teacher_bp = Blueprint("teacher", __name__)


@teacher_bp.route("/create_class", methods=["POST"])
@role_required(1)
def add_class():
    data = request.json or {}
    current_teacher_id = g.current_user_id
    class_name_text = data.get("class_name")
    class_introduce_text = data.get("class_introduce") or ""
    if not class_name_text or not current_teacher_id:
        return jsonify(
            {"code": 400, "msg": "缺少班级名称或教师id！", "data": None}
        ), 400
    if len(class_name_text) > 20:
        return jsonify(
            {"code": 422, "msg": "班级名称字符长度超限！", "data": None}
        ), 422
    if len(class_introduce_text) > 50:
        return jsonify(
            {"code": 422, "msg": "班级介绍字符长度超限！", "data": None}
        ), 422
    new_class = ClassManagement(
        teacher_id=current_teacher_id,
        class_name=class_name_text,
        class_introduce=class_introduce_text,
        create_time=datetime.now(),
    )
    db.session.add(new_class)
    db.session.commit()
    return jsonify({"code": 200, "msg": "创建班级成功！", "data": None})


@teacher_bp.route("/update_class_information", methods=["POST"])
@role_required(1)
def update_class_information():
    data = request.json or {}
    current_class_id = data.get("class_id")
    modified_class_name = data.get("enter_class_name")
    modified_class_introduce = data.get("enter_class_introduce") or ""
    if not current_class_id or not modified_class_name:
        return jsonify({"code": 400, "msg": "缺少必要的班级信息！", "data": None}), 400
    if len(modified_class_name) > 20:
        return jsonify(
            {"code": 422, "msg": "班级名称字符长度超限！", "data": None}
        ), 422
    if len(modified_class_introduce) > 50:
        return jsonify(
            {"code": 422, "msg": "班级介绍字符长度超限！", "data": None}
        ), 422
    current_teacher_id = g.current_user_id
    current_class_object = ClassManagement.query.filter_by(
        class_id=current_class_id, teacher_id=current_teacher_id
    ).first()
    if not current_class_object:
        return jsonify({"code": 404, "msg": "班级不存在！", "data": None}), 404
    current_class_object.class_name = modified_class_name
    current_class_object.class_introduce = modified_class_introduce
    db.session.is_modified(current_class_object)
    db.session.commit()
    return jsonify({"code": 200, "msg": "班级数据修改成功！", "data": None})


@teacher_bp.route("/query_my_classes", methods=["GET", "POST"])
@role_required(1)
def my_classes():
    current_teacher_id = g.current_user_id
    classes_list_object = ClassManagement.query.filter_by(
        teacher_id=current_teacher_id
    ).all()
    if not classes_list_object:
        return jsonify({"code": 200, "msg": "当前无负责的班级", "data": None})
    classes_list = []
    for i in classes_list_object:
        target_dic = {
            "class_id": i.class_id,
            "class_name": i.class_name,
            "class_introduce": i.class_introduce,
        }
        classes_list.append(target_dic)
    return jsonify({"code": 200, "msg": "成功查询到班级！", "data": classes_list})


@teacher_bp.route("/query_class_students", methods=["POST"])
@role_required(1)
def class_students():
    data = request.json.get("class_id")
    class_students_object = User.query.filter_by(class_id=data, role=0).all()
    if not class_students_object:
        return jsonify({"code": 404, "msg": "班级或学生不存在！", "data": None}), 404
    class_students_list = []
    for i in class_students_object:
        class_students_list.append(
            {"student_id": i.user_id, "student_name": i.real_name}
        )
    class_object = ClassManagement.query.filter_by(class_id=data).first()
    return jsonify(
        {
            "code": 200,
            "msg": "成功获得班级数据！",
            "data": {
                "class_name": class_object.class_name,
                "class_introduce": class_object.class_introduce,
                "student_list": class_students_list,
            },
        }
    )


@teacher_bp.route("/delete_class", methods=["POST"])
@role_required(1)
def delete_class():
    data = request.json or {}
    target_class_id = data.get("class_id")
    current_tracher_id = g.current_user_id
    if not target_class_id:
        return jsonify({"code": 400, "msg": "缺少班级id", "data": None}), 400
    target_class = ClassManagement.query.filter_by(
        class_id=target_class_id, teacher_id=current_tracher_id
    ).first()
    if not target_class:
        return jsonify({"code": 404, "msg": "班级不存在或未授权！", "data": None}), 404
    db.session.delete(target_class)
    db.session.commit()
    return jsonify({"code": 200, "msg": "班级已删除！", "data": None})


@teacher_bp.route("/remove_student", methods=["POST"])
@role_required(1)
def remove_student():
    data = request.json or {}
    target_student_id = data.get("student_id")
    current_teacher_id = g.current_user_id
    if not target_student_id:
        return jsonify({"code": 400, "msg": "缺少学生id！", "data": None}), 400
    target_student = User.query.filter_by(user_id=target_student_id).first()
    if not target_student:
        return jsonify({"code": 404, "msg": "学生不存在！", "data": None}), 404
    target_class = ClassManagement.query.filter_by(
        teacher_id=current_teacher_id, class_id=target_student.class_id
    ).first()
    if not target_class:
        return jsonify({"code": 403, "msg": "该学生不在您的班级中！", "data": None})
    target_student.class_id = None
    db.session.is_modified(target_student)
    db.session.commit()
    return jsonify({"code": 200, "msg": "学生删除成功！", "data": None})


@teacher_bp.route("/get_s_interviews_history", methods=["POST"])
@role_required(1)
def get_s_interview_history():
    data = request.json or {}
    current_student_id = data.get("student_id")
    current_teacher_id = g.current_user_id
    current_student = User.query.filter_by(user_id=current_student_id).first()
    if not current_student:
        return jsonify({"code": 404, "msg": "学生不存在！", "data": None}), 404
    target_class_id = current_student.class_id
    target_class = ClassManagement.query.filter_by(
        class_id=target_class_id, teacher_id=current_teacher_id
    ).first()
    if not target_class:
        return jsonify({"code": 404, "msg": "班级不存在！", "data": None}), 404
    target_interview = (
        InterviewRecord.query.filter_by(student_id=current_student.user_id)
        .order_by(InterviewRecord.create_time.desc())
        .all()
    )
    if not target_interview:
        return jsonify({"code": 404, "msg": "当前学生暂无面试记录！", "data": None})
    interview_history_list = []
    for i in target_interview:
        signal_history_dict = {
            "interview_id": i.interview_id,
            "post": i.post,
            "status": i.status,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M")
            if i.create_time
            else "",
        }
        interview_history_list.append(signal_history_dict)
    return jsonify(
        {"code": 200, "msg": "历史记录获取成功！", "data": interview_history_list}
    )


@teacher_bp.route("/get_student_interview", methods=["POST"])
@role_required(1)
def get_student_interview():
    data = request.json or {}
    current_interview_id = data.get("interview_id")
    if not current_interview_id:
        return jsonify({"code": 400, "msg": "缺少面试记录ID！", "data": None}), 400
    current_teacher_id = g.current_user_id
    target_interview = InterviewRecord.query.filter_by(
        interview_id=current_interview_id
    ).first()
    if not target_interview:
        return jsonify({"code": 404, "msg": "面试记录不存在！", "data": None}), 404
    target_student_id = target_interview.student_id
    target_student = User.query.filter_by(user_id=target_student_id).first()
    student_class_id = target_student.class_id
    target_class = ClassManagement.query.filter_by(class_id=student_class_id).first()
    if not target_class:
        return jsonify({"code": 404, "msg": "班级不存在！", "data": None}), 404
    target_teacher_id = target_class.teacher_id
    if str(current_teacher_id) != str(target_teacher_id):
        return jsonify({"code": 403, "msg": "您无权访问！", "data": None}), 403
    detail = {
        "interview_id": target_interview.interview_id,
        "dimension_grade": target_interview.dimension_grade,
        "analysis_text": target_interview.analysis_text,
        "teacher_comment": target_interview.teacher_comment,
        "comment_time": target_interview.comment_time.strftime("%Y-%m-%d %H:%M")
        if target_interview.comment_time
        else "",
        "post": target_interview.post,
    }
    return jsonify({"code": 200, "msg": "成功获取面试详情！", "data": detail})


@teacher_bp.route("/submit_comment", methods=["POST"])
@role_required(1)
def submit_comment():
    data = request.json or {}
    current_interview_id = data.get("interview_id")
    if not current_interview_id:
        return jsonify({"code": 400, "msg": "缺少面试记录ID！", "data": None}), 400
    comment_text = data.get("comment_text")
    if not comment_text:
        return jsonify({"code": 400, "msg": "请输入评论！", "data": None})
    current_teacher_id = g.current_user_id
    target_interview = InterviewRecord.query.filter_by(
        interview_id=current_interview_id
    ).first()
    if not target_interview:
        return jsonify({"code": 404, "msg": "面试记录不存在！", "data": None}), 404
    target_student_id = target_interview.student_id
    target_student = User.query.filter_by(user_id=target_student_id).first()
    student_class_id = target_student.class_id
    target_class = ClassManagement.query.filter_by(class_id=student_class_id).first()
    if not target_class:
        return jsonify({"code": 404, "msg": "班级不存在！", "data": None}), 404
    target_teacher_id = target_class.teacher_id
    if str(current_teacher_id) != str(target_teacher_id):
        return jsonify({"code": 403, "msg": "您无权访问！", "data": None}), 403
    target_interview.teacher_comment = comment_text
    target_interview.comment_time = datetime.now()
    target_interview.status = 3
    db.session.commit()
    return jsonify({"code": 200, "msg": "评论发布成功！", "data": None})
