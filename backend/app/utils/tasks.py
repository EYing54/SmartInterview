import os
import json
import base64
import pathlib
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
    1. 提取题目和前端存入的虚拟音频 URL。
    2. 将 URL 还原为硬盘真实的物理路径。
    3. 调用阿里 ASR 将音频转为真实文本。
    4. 调用文本大模型进行单题评估。
    5. 填入单题成绩、真实文本并完成分析判断。
    6. 若全场结束，调用总结大模型填入总成绩。
    """
    # 1. 准备大模型客户端
    text_client = OpenAI(
        api_key=os.getenv("TEXT_API_KEY"), base_url=os.getenv("TEXT_BASE_URL")
    )

    asr_client = OpenAI(
        api_key=os.getenv("ASR_API_KEY"),
        base_url=os.getenv("ASR_BASE_URL_OpenAI"),
    )

    current_question_text = ""
    audio_url = (
        ""  # 这里拿到的将是形如 /api/media/interview_x/audio/xxx.webm 的虚拟路由
    )
    user_answer_text = ""

    # ---- 阶段一：只读阶段，快速获取题目内容和录音文件 URL ----
    with scheduler.app.app_context():
        target_record = InterviewRecord.query.filter_by(
            interview_id=interview_id
        ).first()

        if not target_record:
            print(f"❌ 未找到面试记录: {interview_id}")
            return

        question_list = target_record.question_record

        for q in question_list:
            if str(q.get("question_id")) == str(question_id):
                current_question_text = q.get("question", "未知题目")
                # 从数据库中取出前端路由视角的 URL 路径
                audio_url = q.get("audio_path", "")
                break

    # 如果没有找到音频路径，使用兜底文本
    if not audio_url:
        print(f"⚠ 警告：单题 {question_id} 未找到录音 URL！")
        user_answer_text = "（系统提示：考生未录音或音频文件丢失）"
    else:
        # ---- 阶段二：将虚拟 Web URL 还原为本地服务器硬盘的真实物理路径，并调用 ASR ----
        try:
            # 1. 从 URL 中安全截取出最终的文件名 (例如 xxx.webm)
            filename = audio_url.split("/")[-1]

            # 2. 从当前 Flask 应用的配置中，动态获取媒体根目录
            base_dir = scheduler.app.config.get("INTERVIEW_MEDIA_DIR")

            if not base_dir:
                raise ValueError("未在系统配置中找到 INTERVIEW_MEDIA_DIR 环境变量")

            # 3. 严格按照视图函数里存储文件时的规则，还原物理绝对路径
            real_audio_disk_path = os.path.join(
                base_dir, f"interview_{interview_id}", "audio", filename
            )

            file_path_obj = pathlib.Path(real_audio_disk_path)

            if file_path_obj.exists():
                print(f"🎙 后台线程已成功定位物理文件，开始转写: {real_audio_disk_path}")

                # 读取本地物理文件字节流并转化为 Base64
                base64_str = base64.b64encode(file_path_obj.read_bytes()).decode()
                audio_mime_type = "audio/webm"
                data_uri = f"data:{audio_mime_type};base64,{base64_str}"

                # 发起转写请求
                asr_completion = asr_client.chat.completions.create(
                    model="qwen3-asr-flash",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_audio",
                                    "input_audio": {"data": data_uri},
                                }
                            ],
                        }
                    ],
                    stream=False,
                    extra_body={"asr_options": {"enable_itn": False}},
                )
                user_answer_text = asr_completion.choices[0].message.content
                print(f"✨ 语音转文字成功: {user_answer_text}")
            else:
                print(
                    f"❌ 物理还原成功，但硬盘上依然不存在该文件: {real_audio_disk_path}"
                )
                user_answer_text = "（系统提示：录音物理文件在服务器中未找到）"

        except Exception as e:
            print(f"❌ 还原路径或呼叫阿里 ASR 发生异常: {e}")
            user_answer_text = "（系统提示：语音识别阶段发生系统故障）"

    # ---- 阶段三：调用文本大模型，针对转写出的真实文本进行技术评估 ----
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
        response = text_client.chat.completions.create(
            model=os.getenv("TEXT_MODEL"),
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

    is_all_finished = False
    interview_context = ""
    total_confident = 0
    total_questions = 0

    # ---- 阶段四：加排他锁更新阶段，写入识别文本、单题分数，并判断整场是否收尾 ----
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
                # 将转写出的真实文本存回数据库，供后续全局统筹大模型和前端展示使用
                q["user_answer_text"] = user_answer_text
                q["ai_single_analysis"] = {
                    "dimension_grade": single_score,
                    "comment": single_comment,
                }
                q["facial_emotion"] = mock_emotion
                break

        flag_modified(target_record, "question_record")

        # 在锁的内部检查是否所有题目均已完成分析
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

    # ---- 阶段五：整场面试结束后的全局统筹大模型分析 ----
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
            response = text_client.chat.completions.create(
                model=os.getenv("TEXT_MODEL"),
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

        # 写入综合性的 AI 分析数据
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
