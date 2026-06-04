import os
import random
from datetime import datetime, timedelta
from sqlalchemy import text
from app import create_app
from extensions import db
from app.models.user import User
from app.models.class_management import ClassManagement
from app.models.record import InterviewRecord, ResumeRecord
from app.models.question import QuestionBank, TagPool, QuestionTagRelation
from app.routes.auth import encrypt_password


def seed_database():
    app = create_app()
    with app.app_context():
        print("🔧 正在使用纯净模式清理旧数据...")
        # 强制关闭外键检查，直接清空数据，完全不碰你的表结构
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

        tables = [
            "question_tag_relation",
            "interview_record",
            "resume_record",
            "question_bank",
            "tag_pool",
            "user",
            "class_management",
        ]

        for table in tables:
            try:
                db.session.execute(text(f"DELETE FROM {table};"))
            except Exception as e:
                print(f"⚠️ 清空 {table} 失败，请确保数据库中已存在该表。")

        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        db.session.commit()

        print("🌱 开始按照最新包含post字段的模型播种数据...")
        common_pwd = encrypt_password("123456")
        stu_pwd = encrypt_password("2460105133")

        # 提前准备好岗位列表
        posts = [
            "Java开发工程师",
            "前端开发工程师",
            "后端开发工程师",
            "全栈工程师",
            "测试工程师",
            "产品经理",
            "UI设计师",
            "运维工程师",
        ]

        # ==========================================
        # 1. 独立创建教师 (此时不需要 class_id)
        # ==========================================
        users_to_add = [
            User(
                username="admin",
                nickname="系统管理员",
                password=common_pwd,
                role=2,
                real_name="管理员",
                avatar_path="",
                create_time=datetime.now(),
            )
        ]

        teachers = []
        for i in range(1, 11):
            t = User(
                username=f"teacher_{i:02d}",
                nickname=f"指导教师{i}",
                password=common_pwd,
                role=1,
                real_name=f"讲师{i}",
                avatar_path="",
                create_time=datetime.now(),
            )
            teachers.append(t)
            users_to_add.append(t)

        db.session.add_all(users_to_add)
        db.session.commit()

        # ==========================================
        # 2. 独立创建班级 (此时绑定上一步生成的 teacher_id)
        # ==========================================
        classes = []
        for i in range(1, 11):
            c = ClassManagement(
                teacher_id=teachers[i - 1].user_id,
                class_name=f"测试虚拟班级_{i:02d}班",
                class_introduce="通用软件开发实训",
                join_rule={"require_audit": False, "max_students": 100},
                create_time=datetime.now(),
            )
            classes.append(c)
        db.session.add_all(classes)
        db.session.commit()

        # ==========================================
        # 3. 批量创建学生 (关键点：在这里把岗位给学生绑上)
        # ==========================================
        students = []

        # 你的主账号：明确绑定 Java 开发
        bonan = User(
            username="2460105133",
            nickname="mikufans",
            password=stu_pwd,
            role=0,
            real_name="realname",
            avatar_path="",
            create_time=datetime.now(),
            class_id=classes[0].class_id,
            post="Java开发工程师",  # 👈 新增字段赋值
        )
        students.append(bonan)

        for i in range(1, 20):
            s = User(
                username=f"stu_{i:03d}",
                nickname=f"测试学员{i}",
                password=common_pwd,
                role=0,
                real_name=f"匿名学员{i}",
                avatar_path="",
                create_time=datetime.now(),
                class_id=random.choice(classes).class_id,
                post=random.choice(posts),  # 👈 匿名学员随机绑定岗位
            )
            students.append(s)
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
            q = QuestionBank(
                question=f"通用技术面试题 {i}：请简述相关底层原理与应用场景？",
                answer=f"参考答案 {i}：需要包含核心概念解释、优缺点对比以及实际业务中的落地案例。",
                is_deleted=0,
                create_time=datetime.now(),
            )
            questions.append(q)
        db.session.add_all(questions)
        db.session.commit()

        relations = []
        for _ in range(30):
            rel = QuestionTagRelation(
                question_id=random.choice(questions).question_id,
                tag_id=random.choice(tags).tag_id,
                create_time=datetime.now(),
            )
            relations.append(rel)
        db.session.add_all(relations)
        db.session.commit()

        # ==========================================
        # 5. 批量创建面试与简历记录
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
            stu = bonan if i < 10 else random.choice(students)
            tchr = random.choice(teachers)

            sampled_qs = random.sample(questions, 3)
            q_record = [
                {
                    "question_id": q.question_id,
                    "question": q.question,
                    "video_path": "",
                    "audio_path": "",
                }
                for q in sampled_qs
            ]

            iv = InterviewRecord(
                student_id=stu.user_id,
                teacher_id=tchr.user_id,
                question_record=q_record,
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
                post=stu.post,  # 👈 历史记录的岗位直接从用户的设定里提取，保持业务一致性
                status=random.choice([0, 1]),
            )
            interviews.append(iv)

            rs = ResumeRecord(
                student_id=stu.user_id,
                teacher_id=tchr.user_id,
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
                post=stu.post,
                status=1,
            )
            resumes.append(rs)

        db.session.add_all(interviews)
        db.session.add_all(resumes)
        db.session.commit()

        print("🎉 完美收工！数据已经装填完毕，所有学生账号都自带了默认岗位。")


if __name__ == "__main__":
    seed_database()
