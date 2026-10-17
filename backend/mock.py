# python mock.py           仅创建缺失的表并补充岗位数据
# python mock.py --reset   清空相关测试表，重新生成整套测试数据


import argparse
import random
from datetime import datetime, timedelta

from app import create_app
from app.models import (
    ClassManagement,
    InterviewRecord,
    JobPosition,
    QuestionBank,
    QuestionTagRelation,
    ResumeRecord,
    TagPool,
    User,
)
from app.utils.encrypt import encrypt_password
from extensions import db
from sqlalchemy import text

# 仅用于初始化测试数据；正式功能应通过岗位表查询，而不是读取这个列表。
JOB_NAMES = [
    "Java开发工程师",
    "前端开发工程师",
    "后端开发工程师",
    "全栈工程师",
    "测试工程师",
    "产品经理",
    "UI设计师",
    "运维工程师",
]


# 原脚本涉及的表，加上新建的岗位表。
TEST_TABLES = [
    "question_tag_relation",
    "interview_record",
    "resume_record",
    "question_bank",
    "tag_pool",
    "user",
    "class_management",
    "job_position",
]


def seed_job_positions():
    """只补充缺失的岗位，重复运行不会插入同名岗位，也不修改已有状态。"""
    existing_names = {name for (name,) in db.session.query(JobPosition.job_name).all()}
    new_jobs = [
        JobPosition(job_name=name, is_enabled=1)
        for name in JOB_NAMES
        if name not in existing_names
    ]
    if new_jobs:
        db.session.add_all(new_jobs)
        db.session.commit()
    print(
        f"岗位初始化完成：新增 {len(new_jobs)} 个，当前共有 {JobPosition.query.count()} 个岗位。"
    )


def clear_test_tables():
    """重置演示数据。必须显式使用 --reset 才会调用。"""
    print("⚠️ 正在清空原有测试数据（包括用户、面试记录等）...")
    # MySQL 上关闭外键检查后再清空；不使用 DROP TABLE，保留表结构。
    with db.engine.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        try:
            for table_name in TEST_TABLES:
                connection.execute(text(f"DELETE FROM `{table_name}`"))
        finally:
            # 无论清理是否成功，都在连接返回连接池前恢复外键检查。
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    print("原有测试数据已清空。")


def seed_demo_data():
    """保留原 mock 的教师、班级、学生、题库和历史记录生成逻辑。"""
    common_pwd = encrypt_password("123456")
    stu_pwd = encrypt_password("2460105133")

    # ==========================================
    # 1. 创建管理员和教师
    # ==========================================
    users_to_add = [
        User(
            username="admin2026",
            nickname="系统管理员",
            password=common_pwd,
            role=2,
            real_name="管理员",
            avatar_path="",
            create_time=datetime.now(),
            is_deleted=0,
        )
    ]

    teachers = []
    for i in range(1, 11):
        teacher = User(
            username=f"teacher_{i:02d}",
            nickname=f"指导教师{i}",
            password=common_pwd,
            role=1,
            real_name=f"讲师{i}",
            avatar_path="",
            create_time=datetime.now(),
            is_deleted=0,
        )
        teachers.append(teacher)
        users_to_add.append(teacher)

    db.session.add_all(users_to_add)
    db.session.commit()

    # ==========================================
    # 2. 创建班级
    # ==========================================
    classes = []
    for i in range(1, 11):
        classroom = ClassManagement(
            teacher_id=teachers[i - 1].user_id,
            class_name=f"测试虚拟班级_{i:02d}班",
            class_introduce="通用软件开发实训",
            create_time=datetime.now(),
        )
        classes.append(classroom)
    db.session.add_all(classes)
    db.session.commit()

    # ==========================================
    # 3. 创建学生（User.post 仍然存岗位名称）
    # ==========================================
    students = []
    bonan = User(
        username="2460105133",
        nickname="mikufans",
        password=stu_pwd,
        role=0,
        real_name="realname",
        avatar_path="",
        create_time=datetime.now(),
        class_id=classes[0].class_id,
        post="Java开发工程师",
        is_deleted=0,
    )
    students.append(bonan)

    for i in range(1, 20):
        student = User(
            username=f"stu_{i:03d}",
            nickname=f"测试学员{i}",
            password=common_pwd,
            role=0,
            real_name=f"匿名学员{i}",
            avatar_path="",
            create_time=datetime.now(),
            class_id=random.choice(classes).class_id,
            post=random.choice(JOB_NAMES),
            is_deleted=0,
        )
        students.append(student)
    db.session.add_all(students)
    db.session.commit()

    # ==========================================
    # 4. 创建题库与标签
    # ==========================================
    tags = [
        TagPool(tag_name=name, create_time=datetime.now())
        for name in [
            "Java基础",
            "前端框架",
            "数据库",
            "计算机网络",
            "操作系统",
            "算法与数据结构",
            "系统架构",
            "软技能",
        ]
    ]
    db.session.add_all(tags)
    db.session.commit()

    questions = []
    for i in range(1, 21):
        question = QuestionBank(
            question=f"通用技术面试题 {i}：请简述相关底层原理与应用场景？",
            answer=f"参考答案 {i}：需要包含核心概念解释、优缺点对比以及实际业务中的落地案例。",
            is_deleted=0,
            create_time=datetime.now(),
        )
        questions.append(question)
    db.session.add_all(questions)
    db.session.commit()

    relations = []
    for _ in range(30):
        relation = QuestionTagRelation(
            question_id=random.choice(questions).question_id,
            tag_id=random.choice(tags).tag_id,
            create_time=datetime.now(),
        )
        relations.append(relation)
    db.session.add_all(relations)
    db.session.commit()

    # ==========================================
    # 5. 创建面试与简历记录
    # ==========================================
    feedbacks = [
        "基础扎实，表达流畅。",
        "逻辑清晰，但深度欠缺。",
        "实战经验丰富，建议加强理论。",
        "沟通能力优秀，技术方案合理。",
    ]
    interviews = []
    resumes = []

    for i in range(25):
        student = bonan if i < 10 else random.choice(students)
        teacher = random.choice(teachers)
        sampled_questions = random.sample(questions, 3)
        question_record = [
            {
                "question_id": q.question_id,
                "question": q.question,
                "video_path": "",
                "audio_path": "",
            }
            for q in sampled_questions
        ]

        interview = InterviewRecord(
            student_id=student.user_id,
            teacher_id=teacher.user_id,
            question_record=question_record,
            create_time=datetime.now() - timedelta(days=random.randint(1, 30)),
            dimension_grade={
                "技术深度": random.randint(60, 95),
                "业务理解": random.randint(60, 95),
                "沟通表达": random.randint(60, 95),
                "逻辑思维": random.randint(60, 95),
                "抗压能力": random.randint(60, 95),
            },
            analysis_text=f"AI综合评估：{random.choice(feedbacks)}",
            teacher_comment=f"教师人工复核评语：{random.choice(feedbacks)}",
            comment_time=datetime.now() - timedelta(hours=random.randint(1, 24)),
            post=student.post,
            status=random.choice([0, 1]),
        )
        interviews.append(interview)

        resume = ResumeRecord(
            student_id=student.user_id,
            teacher_id=teacher.user_id,
            create_time=datetime.now() - timedelta(days=random.randint(1, 10)),
            dimension_grade={
                "排版美观": random.randint(70, 100),
                "项目经验": random.randint(70, 100),
                "专业技能": random.randint(70, 100),
            },
            file_path=f"/static/resumes/dummy_resume_{i}.pdf",
            analysis_text=f"简历诊断：结构完整，{random.choice(feedbacks)}",
            teacher_comment="建议补充更多量化数据。",
            comment_time=datetime.now(),
            post=student.post,
            status=1,
        )
        resumes.append(resume)

    db.session.add_all(interviews)
    db.session.add_all(resumes)
    db.session.commit()
    print("完整测试数据初始化完成。")


def seed_database(reset=False):
    app = create_app()
    with app.app_context():
        # 需要先导入 JobPosition（已在本文件顶部导入），create_all 才能识别它。
        # create_all 只创建缺失的表，不会覆盖已有表结构或删除已有数据。
        db.create_all()
        if reset:
            clear_test_tables()
        seed_job_positions()
        if reset:
            seed_demo_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SmartInterview 测试数据初始化")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="清空并重新生成全套测试数据（会删除现有用户和面试记录）",
    )
    args = parser.parse_args()
    seed_database(reset=args.reset)
