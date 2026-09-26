import base64
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def test_video_analysis(video_path: str):
    # 1. 校验文件是否存在
    if not os.path.exists(video_path):
        print(f"找不到视频文件：{video_path}")
        return

    print("正在将本地视频转换为 Base64 编码，请稍候...")

    # 【核心转换】：读取物理文件 -> 转为二进制流 -> Base64编码 -> 拼接成Data URI格式
    with open(video_path, "rb") as f:
        base64_data = base64.b64encode(f.read()).decode("utf-8")

    # 既然先测试mp4，MIME类型就是 video/mp4 (如果是webm，就是 video/webm)
    video_data_uri = f"data:video/mp4;base64,{base64_data}"

    # 2. 初始化客户端
    client = OpenAI(api_key=os.getenv("VL_API_KEY"), base_url=os.getenv("VL_BASE_URL"))

    print("正在使用 Qwen3-VL-Flash 分析视频...")

    # 3. 发起多模态请求
    try:
        completion = client.chat.completions.create(
            model=os.getenv("VL_MODEL"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            # 【注意这里】：类型变为了 video_url
                            "type": "video_url",
                            "video_url": {"url": video_data_uri},
                        },
                        {
                            "type": "text",
                            "text": "请分析这段面试视频中，考生的面部微表情、情绪状态以及肢体动作，判断他是否自信或紧张。",
                        },
                    ],
                },
            ],
            stream=True,
            # 开启思考过程
            extra_body={"enable_thinking": True, "thinking_budget": 81920},
        )

        reasoning_content = ""
        answer_content = ""
        is_answering = False

        print("\n" + "=" * 20 + " 思考过程 " + "=" * 20 + "\n")

        for chunk in completion:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 打印思考过程
            if (
                hasattr(delta, "reasoning_content")
                and delta.reasoning_content is not None
            ):
                print(delta.reasoning_content, end="", flush=True)
                reasoning_content += delta.reasoning_content
            else:
                # 思考结束，开始正式回复
                if (
                    delta.content != ""
                    and delta.content is not None
                    and not is_answering
                ):
                    print("\n\n" + "=" * 20 + " 最终分析结论 " + "=" * 20 + "\n")
                    is_answering = True

                if delta.content:
                    print(delta.content, end="", flush=True)
                    answer_content += delta.content

        print("\n\n分析完成！")

    except Exception as e:  # noqa: BLE001
        print(f"\n请求发生异常：{e}")


if __name__ == "__main__":
    # 填入你本地真实存在的 mp4 视频绝对路径
    test_video = r"E:\Project\SmartInterview\test_exapmle\lv_test_file\Video-Interviewing-Example.mp4"
    test_video_analysis(test_video)
