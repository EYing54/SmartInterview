import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
from extensions import db, scheduler
from app.models.record import InterviewRecord
from sqlalchemy.orm.attributes import flag_modified


# 每45分钟删除一次数据库里面试记录状态码为0的记录
@scheduler.task("interval", id="clean_dirty_interview", minutes=45)
def clean_dirty_interview():
    with scheduler.app.app_context():
        one_hour_ago = datetime.now() - timedelta(hours=1)

        deleted_count = InterviewRecord.query.filter(
            InterviewRecord.status == 0, InterviewRecord.create_time < one_hour_ago
        ).delete(synchronize_session=False)

        db.session.commit()
        print(f"[{datetime.now()}] 清理了{deleted_count}条数据！")


def process_single_question(interview_id, question_id):
    """
    单题异步处理函数：
    1. 提取题目和答案。
    2. 调用单题大模型。
    3. 填入单题成绩并完成分析判断。
    4. 调用总结用的大模型（长耗时）。
    5. 填入总成绩。
    """
    # 提前准备好大模型客户端
    client = OpenAI(api_key=os.getenv("AI_API_KEY"), base_url=os.getenv("AI_BASE_URL"))
    # 提取目标题目的id和回答内容
    current_question_text = ""
    user_answer_text = ""
    with scheduler.app.app_context():
        target_record = InterviewRecord.query.filter_by(
            interview_id=interview_id
        ).first()

        if not target_record:
            return

        question_list = target_record.question_record

        for q in question_list:
            if str(q.get("question_id")) == str(question_id):
                current_question_text = q.get("question", "未知题目")
                # 假数据，后续引入语音转文字
                user_answer_text = "我觉得这道题的核心是高并发处理，可以通过引入 Redis 缓存来解决，同时要注意数据一致性的问题。"
                break
    # 调整大模型
    single_system_prompt = """你是一个严苛的技术面试官。
请根据题目和考生的回答，进行单道题目的评估。你需要犀利地指出回答中的错误、遗漏或亮点。
你必须严格按照以下 JSON 格式输出结果：
{
    "dimension_grade": {
        "专业技能": 85,
        "沟通表达": 80,
        "逻辑思维": 75,
        "综合分数": 80
    },
    "comment": "这里写一句简短犀利的单题点评，50字以内。"
}"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("AI_MODEL"),
            messages=[
                {"role": "system", "content": single_system_prompt},
                {
                    "role": "user",
                    "content": f"题目：{current_question_text}\n考生回答：{user_answer_text}",
                },
            ],
            response_format={"type": "json_object"},
        )

        ai_result = json.loads(response.choices[0].message.content)
        print(ai_result)
        single_score = ai_result.get(
            "dimension_grade",
            {"专业技能": 0, "沟通表达": 0, "逻辑思维": 0, "综合分数": 0},
        )
        single_comment = ai_result.get("comment", "单题分析失败。")

    except Exception as e:
        print(f"❌ 单题 AI 分析失败 (题目ID: {question_id}): {e}")
        single_score = {"专业技能": 0, "沟通表达": 0, "逻辑思维": 0, "综合分数": 0}
        single_comment = "单题分析出现异常。"

    # 假的面部分析数据
    mock_emotion = {"confident_score": 85, "nervous_score": 15}

    # 声明跨越生命周期的控制变量，用于向后面的全局大模型接力
    is_all_finished = False
    interview_context = ""
    total_confident = 0
    total_questions = 0
    with scheduler.app.app_context():
        target_record = (
            InterviewRecord.query.filter_by(interview_id=interview_id)
            .with_for_update()
            .first()
        )

        if not target_record:
            return

        question_list = target_record.question_record

        # 填入单题数据
        for q in question_list:
            if str(q.get("question_id")) == str(question_id):
                q["ai_single_analysis"] = {
                    "dimension_grade": single_score,
                    "comment": single_comment,
                }
                q["facial_emotion"] = mock_emotion
                break

        flag_modified(target_record, "question_record")

        # 在锁的内部查岗，防止并发
        is_all_finished = True
        for q in question_list:
            if "ai_single_analysis" not in q or "facial_emotion" not in q:
                is_all_finished = False
                break

        # 如果当前线程是填完最后一个数据的，在锁内安全整合总体数据
        if is_all_finished:
            total_questions = len(question_list)
            for index, q in enumerate(question_list):
                q_text = q.get("question", "未知题目")
                ans_text = q.get("user_answer_text", "无回答")
                comment = q.get("ai_single_analysis", {}).get("comment", "无评价")

                total_confident += q.get("facial_emotion", {}).get("confident_score", 0)
                interview_context += (
                    f"### 【第 {index + 1} 题】\n题目：{q_text}\n考生回答：{ans_text}\n单题分析：{comment}\n"
                    + "-" * 30
                    + "\n\n"
                )
        db.session.commit()

    # 最后的完整分析的大模型
    if is_all_finished:
        print("🎉 10道题数据全部收集完毕！正在呼叫全局 AI 进行最后统筹...")

        global_system_prompt = """你是一个严苛且专业的资深技术面试官。
请根据提供的【面试全过程记录】，综合评估考生的表现。你需要自行提炼出最能概括该考生水平的 4-5 个评估维度。
注意：必须包含"专业技能"、"沟通表达"、"逻辑思维"这三项基础维度，并根据考生的实际表现动态新增 1-2 项专属维度（如"抗压能力"、"工程素养"等）。

你必须严格按照以下 JSON 格式输出结果：
{
    "dimension_grade": {
        "专业技能": 85,
        "沟通表达": 80,
        "逻辑思维": 75,
        "这里替换为新增动态维度名": 80,
        "综合分数": 80
    },
    "analysis_text": "这里写一段500字左右的全局综合评语，犀利指出核心优缺点。"
}"""

        try:
            response = client.chat.completions.create(
                model=os.getenv("AI_MODEL"),
                messages=[
                    {"role": "system", "content": global_system_prompt},
                    {
                        "role": "user",
                        "content": f"【面试全过程记录】\n{interview_context}",
                    },
                ],
                response_format={"type": "json_object"},
            )

            ai_result = json.loads(response.choices[0].message.content)
            final_dimension_grade = ai_result.get("dimension_grade", {})

            # 融合面部识别的心理素质分
            final_dimension_grade["心理素质"] = total_confident / total_questions
            global_comment = ai_result.get("analysis_text", "全局分析生成失败。")

        except Exception as e:
            print(f"❌ 全局 AI 分析发生异常: {e}")
            final_dimension_grade = {"分析失败": 0}
            global_comment = "全局分析超时或异常。"
        # 写入综合性的ai分析的数据
        with scheduler.app.app_context():
            final_record = (
                InterviewRecord.query.filter_by(interview_id=interview_id)
                .with_for_update()
                .first()
            )

            if final_record:
                final_record.dimension_grade = final_dimension_grade
                final_record.analysis_text = global_comment
                final_record.status = 2

                flag_modified(final_record, "dimension_grade")
                db.session.commit()
                print("✅ 完美交卷！动态维度和综合评语已存入数据库！")
