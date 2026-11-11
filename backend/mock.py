# python mock.py           检查并补充数据库结构、岗位数据
# python mock.py --reset   清空并重新生成整套测试数据（危险操作）

import argparse
import random
from datetime import datetime, timedelta
from itertools import product

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
from sqlalchemy import inspect, text

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


def ensure_tag_pool_schema():
    """检查标签池表结构，补充缺失的 is_deleted 字段。"""
    inspector = inspect(db.engine)

    columns = {column["name"] for column in inspector.get_columns("tag_pool")}

    if "is_deleted" not in columns:
        print("检测到 tag_pool 缺少 is_deleted 字段，正在补充...")

        with db.engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE `tag_pool` "
                    "ADD COLUMN `is_deleted` TINYINT NOT NULL DEFAULT 0"
                )
            )

        print("tag_pool.is_deleted 字段添加成功！")
    else:
        print("tag_pool.is_deleted 字段已存在，无需修改。")


def ensure_question_tag_unique_constraint():
    """确保同一道题目不能重复关联同一个标签。"""
    inspector = inspect(db.engine)
    table_name = "question_tag_relation"
    target_columns = {"question_id", "tag_id"}

    # 检查已经存在的唯一约束
    constraints = inspector.get_unique_constraints(table_name)
    indexes = inspector.get_indexes(table_name)

    has_constraint = any(
        set(item.get("column_names") or []) == target_columns for item in constraints
    )

    has_unique_index = any(
        item.get("unique", False)
        and set(item.get("column_names") or []) == target_columns
        for item in indexes
    )

    if has_constraint or has_unique_index:
        print("题目标签联合唯一约束已存在，无需修改。")
        return

    # 添加约束前，检查数据库是否已经存在重复关联
    with db.engine.connect() as connection:
        duplicates = (
            connection.execute(
                text(
                    """
                SELECT question_id, tag_id, COUNT(*) AS duplicate_count
                FROM question_tag_relation
                GROUP BY question_id, tag_id
                HAVING COUNT(*) > 1
                LIMIT 5
                """
                )
            )
            .mappings()
            .all()
        )

    if duplicates:
        examples = [(row["question_id"], row["tag_id"]) for row in duplicates]
        raise RuntimeError(
            "检测到重复的题目标签关联，无法添加唯一约束。"
            f"重复组合示例：{examples}。"
            "请先清理重复记录；不要直接重置重要数据。"
        )

    # MariaDB：为现有表添加联合唯一约束
    with db.engine.begin() as connection:
        connection.execute(
            text(
                """
                ALTER TABLE `question_tag_relation`
                ADD CONSTRAINT `uq_question_tag`
                UNIQUE (`question_id`, `tag_id`)
                """
            )
        )

    print("题目标签联合唯一约束添加成功！")


def seed_job_positions():
    """只补充缺失的岗位，不修改已有岗位。"""
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
        f"岗位初始化完成：新增 {len(new_jobs)} 个，"
        f"当前共有 {JobPosition.query.count()} 个岗位。"
    )


def clear_test_tables():
    """只有显式使用 --reset 才会清空测试数据。"""
    print("警告：正在清空原有测试数据，包括用户和面试记录！")

    with db.engine.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        try:
            for table_name in TEST_TABLES:
                connection.execute(text(f"DELETE FROM `{table_name}`"))
        finally:
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    print("原有测试数据已清空。")


def seed_demo_data():
    """生成教师、班级、学生、题库和历史记录测试数据。"""

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
    # 3. 创建学生
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
        TagPool(
            tag_name=name,
            is_deleted=0,
            create_time=datetime.now(),
        )
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
            answer=(
                f"参考答案 {i}：需要包含核心概念解释、"
                "优缺点对比以及实际业务中的落地案例。"
            ),
            is_deleted=0,
            create_time=datetime.now(),
        )
        questions.append(question)

    db.session.add_all(questions)
    db.session.commit()

    # 生成不重复的题目与标签组合
    all_pairs = list(product(questions, tags))
    selected_pairs = random.sample(all_pairs, k=30)

    relations = []

    for question, tag in selected_pairs:
        relation = QuestionTagRelation(
            question_id=question.question_id,
            tag_id=tag.tag_id,
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
        db.create_all()

        ensure_tag_pool_schema()

        if reset:
            clear_test_tables()

        # 同步现有数据库中的联合唯一约束
        ensure_question_tag_unique_constraint()

        seed_job_positions()

        if reset:
            seed_demo_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SmartInterview 测试数据初始化")

    parser.add_argument(
        "--reset",
        action="store_true",
        help="清空并重新生成全套测试数据",
    )

    args = parser.parse_args()
    seed_database(reset=args.reset)
