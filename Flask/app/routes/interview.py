from datetime import datetime
import random
from flask import Blueprint, jsonify, request
from Flask.app.models.user import User
from app.models.record import InterviewRecord
from app.models.question import QuestionBank
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
        return jsonify({"code": 404, "msg": "用户不存在", "data": None})
    post_text = data.get("post")
    if not post_text:
        return jsonify({"code": 404, "msg": "未选择岗位", "data": None})
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
            "code": 200,
            "msg": "面试记录已创建！",
            "data": {"interview_id": new_interview_record.interview_id},
        }  # 向前端返回面试记录的id
    )
