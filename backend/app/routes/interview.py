import os
from datetime import datetime
import random
from flask import Blueprint, current_app, jsonify, request, g
from app.models.user import User
from app.models.record import InterviewRecord
from app.models.question import QuestionBank
from sqlalchemy.orm.attributes import flag_modified
from extensions import db
from app.utils.auth import role_required

interview_bp = Blueprint("interview", __name__)


@interview_bp.route("/create_interview", methods=["POST"])  # 点击“开始面试”时调用该路由
@role_required(0)
def create_interview():
    user_id_text = g.current_user_id
    current_user = User.query.filter_by(user_id=user_id_text).first()
    if not current_user:
        return jsonify({"code": 404, "msg": "用户不存在", "data": None}), 404
    user_post = current_user.post
    if not user_post:
        return jsonify({"code": 400, "msg": "未选择岗位", "data": None}), 400
    target_ids = (
        QuestionBank.query.with_entities(QuestionBank.question_id)
        .filter_by(is_deleted=0)
        .all()
    )  # 获取有效索引
    vaild_ids = []  # 有效索引
    for i in target_ids:
        target_id = i[0]
        vaild_ids.append(target_id)
    selected_ids = random.sample(vaild_ids, 10)  # 随机获取十道题目的id
    target_questions = QuestionBank.query.filter(
        QuestionBank.question_id.in_(selected_ids)
    ).all()  # 获取对应id的题目
    vaild_questions = []  # 有效题目
    for i in target_questions:
        target_question = i.question
        question_id = i.question_id
        vaild_questions.append(
            {
                "question_id": question_id,
                "question": target_question,
            }  # 有效题目包含题目id和题目本身
        )
    new_interview_record = InterviewRecord(
        student_id=user_id_text,
        post=user_post,
        create_time=datetime.now(),
        question_record=vaild_questions,
        status=0,
    )
    db.session.add(new_interview_record)
    db.session.commit()
    return jsonify(
        {
            "code": 201,
            "msg": "面试记录已创建！",
            "data": {
                "interview_id": new_interview_record.interview_id,
                "questions": vaild_questions,
            },
        }  # 向前端返回面试记录的id
    )


@interview_bp.route("/upload_answer", methods=["POST"])
@role_required(0)
def upload_answer():
    vaild_interview_id = request.form.get("interview_id")  # 从前端获取有效的面试id
    vaild_question_id = request.form.get("question_id")  # 从前端获取有效的题目id
    vaild_audio = request.files.get("audio")  # 从前端获取有效的音频文件
    vaild_video = request.files.get("video")  # 从前端获取有效的视频文件
    base_dir = current_app.config.get("INTERVIEW_MEDIA_DIR")
    if not base_dir:
        return jsonify(
            {"code": 500, "msg": "服务器未配置媒体存储路径！", "data": None}
        ), 500

    time = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"{vaild_interview_id}_{vaild_question_id}_{time}.webm"
    video_filename = f"{vaild_interview_id}_{vaild_question_id}_{time}.webm"
    audio_save_dir = os.path.join(base_dir, f"interview_{vaild_interview_id}", "audio")
    video_save_dir = os.path.join(base_dir, f"interview_{vaild_interview_id}", "video")
    # 创建文件夹
    os.makedirs(audio_save_dir, exist_ok=True)
    os.makedirs(video_save_dir, exist_ok=True)
    audio_save_path = os.path.join(audio_save_dir, audio_filename)
    video_save_path = os.path.join(video_save_dir, video_filename)
    if vaild_audio:
        vaild_audio.save(audio_save_path)  # 如果存在音频文件则进行储存
    if vaild_video:
        vaild_video.save(video_save_path)  # 如果存在视频文件则进行储存
    target_record = InterviewRecord.query.filter_by(
        interview_id=vaild_interview_id
    ).first()
    question_list = (
        target_record.question_record
    )  # 开始向数据库中存题目对应的音视频路径
    for q in question_list:
        if str(q.get("question_id")) == str(vaild_question_id):
            if vaild_audio:
                q["audio_path"] = (
                    f"/api/media/interview_{vaild_interview_id}/audio/{audio_filename}"
                )
            if vaild_video:
                q["video_path"] = (
                    f"/api/media/interview_{vaild_interview_id}/video/{video_filename}"
                )
            break
    flag_modified(target_record, "question_record")
    db.session.commit()
    return jsonify({"code": 200, "msg": "回答上传成功！", "data": None})


@interview_bp.route("/finish_interview", methods=["POST"])
@role_required(0)
def finish_answer():
    data = request.json
    target_interview_id = data.get("interview_id")
    target_interview = InterviewRecord.query.filter_by(
        interview_id=target_interview_id
    ).first()
    if not target_interview:
        return jsonify({"code": 404, "msg": "id不存在！", "data": None})
    target_interview.status = 1
    target_interview.dimension_grade = {
        "专业技能": 85,
        "沟通表达": 90,
        "逻辑思维": 80,
        "综合分数": 88,
    }  # 假数据
    target_interview.analysis_text = (
        "表现不错，但在一些基础概念的解释上还需巩固。"  # 假数据
    )
    db.session.commit()
    return jsonify({"code": 200, "msg": "面试已结束", "data": None})


@interview_bp.route("/get_interview_history", methods=["GET"])
@role_required(0)
def get_interview_history():
    current_student_id = g.current_user_id
    records = InterviewRecord.query.filter_by(student_id=current_student_id).all()
    records_list = []
    for i in records:
        single_record_dict = {
            "interview_id": i.interview_id,
            "post": i.post,
            "status": i.status,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M")
            if i.create_time
            else "",
        }
        records_list.append(single_record_dict)
    return jsonify({"code": 200, "msg": "历史记录获取成功！", "data": records_list})


@interview_bp.route("/get_interview_detail", methods=["GET"])
@role_required(0)
def get_interview_detail():
    target_id = request.args.get("interview_id")
    current_student_id = g.current_user_id
    target_interview_detail = InterviewRecord.query.filter_by(
        student_id=current_student_id, interview_id=target_id
    ).first()
    if not target_interview_detail:
        return jsonify({"code": 404, "msg": "id不存在！", "data": None})
    detail = {
        "interview_id": target_interview_detail.interview_id,
        "dimension_grade": target_interview_detail.dimension_grade,
        "analysis_text": target_interview_detail.analysis_text,
        "teacher_comment": target_interview_detail.teacher_comment,
        "comment_time": target_interview_detail.comment_time.strftime("%Y-%m-%d %H:%M")
        if target_interview_detail.comment_time
        else "",
        "post": target_interview_detail.post,
    }
    return jsonify({"code": 200, "msg": "成功获取面试详情！", "data": detail})


@interview_bp.route("/abort_interview", methods=["POST"])
@role_required(0)
def abort_interview():
    data = request.json
    current_interview_id = data.get("interview_id")
    if not current_interview_id:
        return jsonify({"code": 400, "msg": "缺少interview_id！", "data": None})
    target_interview = InterviewRecord.query.filter_by(
        interview_id=current_interview_id
    ).first()
    if not target_interview:
        return jsonify({"code": 404, "msg": "interview_id不存在！", "data": None})
    db.session.delete(target_interview)
    db.session.commit()
    return jsonify({"code": 200, "msg": "无效面试记录已删除", "data": None})
