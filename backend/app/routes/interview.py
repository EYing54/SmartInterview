import os
from datetime import datetime
import random
from flask import Blueprint, jsonify, request
from app.models.user import User
from app.models.record import InterviewRecord
from app.models.question import QuestionBank
from sqlalchemy.orm.attributes import flag_modified
from extensions import db

interview_bp = Blueprint("interview", __name__)


@interview_bp.route(
    "/create_interview", methods=["GET", "POST"]
)  # 点击“开始面试”时调用该路由
def create_interview():
    data = request.json
    student_id_text = data.get("student_id")
    target_student_id = User.query.filter_by(user_id=student_id_text).first()
    if not target_student_id:
        return jsonify({"code": 404, "msg": "用户不存在", "data": None}), 404
    post_text = data.get("post")
    if not post_text:
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
        student_id=student_id_text,
        post=post_text,
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
def upload_answer():
    vaild_interview_id = request.form.get("interview_id")  # 从前端获取有效的面试id
    vaild_question_id = request.form.get("question_id")  # 从前端获取有效的题目id
    vaild_audio = request.files.get("audio")  # 从前端获取有效的音频文件
    vaild_video = request.files.get("video")  # 从前端获取有效的视频文件

    time = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"{vaild_interview_id}_{vaild_question_id}_{time}.mp3"
    video_filename = f"{vaild_interview_id}_{vaild_question_id}_{time}.mp4"
    audio_save_dir = os.path.join(
        "app", "static", f"interview_{vaild_interview_id}", "audio"
    )
    video_save_dir = os.path.join(
        "app", "static", f"interview_{vaild_interview_id}", "video"
    )
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
                    f"/static/interview_{vaild_interview_id}/audio/{audio_filename}"
                )
            if vaild_video:
                q["video_path"] = (
                    f"/static/interview_{vaild_interview_id}/video/{video_filename}"
                )
            break
    flag_modified(target_record, "question_record")
    db.session.commit()
    return jsonify({"code": 200, "msg": "回答上传成功！", "data": None})


"""下一步：@interview_bp.route("/finish_answer",method = ["POST"])"""
