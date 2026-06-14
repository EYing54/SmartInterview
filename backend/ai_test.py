import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("AI_API_KEY"), base_url=os.getenv("AI_BASE_URL"))


def test_ai_grader(question: str, student_answer: str):
    # System Prompt（系统提示词）
    system_prompt = """你是一个严苛且专业的资深技术面试官。
请根据提供的【面试题目】和【考生的文字回答】，对考生的表现进行评估。

你必须严格按照以下 JSON 格式输出结果，绝不能包含任何多余的解释文字或 Markdown 标记：
{
    "dimension_grade": {
        "专业技能": 85,
        "沟通表达": 80,
        "逻辑思维": 75,
        "综合分数": 80
    },
    "analysis_text": "这里写一段100字左右的综合评语，指出优点和不足以及对用户的建议。"
}"""

    # 把真实的题目和学生的回答拼装起来
    user_prompt = f"【面试题目】：{question}\n\n【考生的文字回答】：{student_answer}"

    print("正在进行打分...")

    response = client.chat.completions.create(
        model=os.getenv("AI_MODEL"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        # 强制大模型以 JSON 格式输出
        response_format={"type": "json_object"},
    )

    # 提取结果并尝试解析为 Python 字典
    raw_result = response.choices[0].message.content
    print("📥 AI 原始回复：\n", raw_result)

    try:
        json_data = json.loads(raw_result)
        print("\n✅ 成功解析为字典！")
        print(f"📊 提取到的专业技能分数：{json_data['dimension_grade']['专业技能']}")
        print(f"📝 提取到的评语：{json_data['analysis_text']}")
    except Exception as e:
        print("\n❌ JSON 解析失败，大模型没有按格式输出：", e)


if __name__ == "__main__":
    q = "请简述一下 HTTP 和 HTTPS 的区别。"
    ans = "一个有s一个没s"
    test_ai_grader(q, ans)
