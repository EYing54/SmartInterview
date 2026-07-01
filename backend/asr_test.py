import os
import base64
import pathlib
from openai import OpenAI
from dotenv import load_dotenv

# 1. 强行加载当前目录下的 .env 文件，让 os.getenv 能成功读到你的 API_KEY
load_dotenv()


def test_qwen_asr_with_base64():
    # ================= 必须修改的配置 =================
    # 请替换为你本地真实存在的 webm 文件绝对路径
    file_path = r"E:\music\Till the Sky Falls Down .m4a"
    # ==================================================

    # 针对前端 WebRTC 的原生录音，MIME 类型通常是 audio/webm
    audio_mime_type = "audio/mp4"

    file_path_obj = pathlib.Path(file_path)
    if not file_path_obj.exists():
        print(f"❌ 找不到音频文件，请仔细检查路径是否拼写正确: {file_path}")
        return

    print("1. 正在读取本地录音并进行 Base64 编码...")
    # 核心转换逻辑：读取物理文件 -> 提取二进制流 -> 翻译成 Base64 字符串 -> 拼接成大模型认识的信封格式
    base64_str = base64.b64encode(file_path_obj.read_bytes()).decode()
    data_uri = f"data:{audio_mime_type};base64,{base64_str}"

    print("2. 正在初始化 OpenAI 兼容客户端...")
    client = OpenAI(
        api_key=os.getenv("ASR_API_KEY"),
        base_url=os.getenv("ASR_BASE_URL_OpenAI"),
    )

    print("3. 正在将音频数据发送至 qwen3-asr-flash 接口进行转写，请稍候...")
    try:
        completion = client.chat.completions.create(
            model=os.getenv("ASR_MODEL"),
            messages=[
                {
                    "content": [
                        {"type": "input_audio", "input_audio": {"data": data_uri}}
                    ],
                    "role": "user",
                }
            ],
            stream=False,
            extra_body={
                "asr_options": {
                    "enable_itn": False  # 保持文字原貌，不强制转换数字
                }
            },
        )

        # 提取并打印最终的文字结果
        print("\n================ 识别成功 ================")
        print(completion.choices[0].message.content)
        print("==========================================\n")

    except Exception as e:
        print(f"\n❌ 请求报错了，错误详情：{e}")


if __name__ == "__main__":
    test_qwen_asr_with_base64()
