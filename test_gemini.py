import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODELS_TO_TRY = [
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-flash-latest",
]

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY", ""),
    timeout=60,
    max_retries=0,  # không tự thử lại, để thấy lỗi thật
)

for model in MODELS_TO_TRY:
    print(f"\n--- Thử: {model}")
    start = time.time()
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Chào bạn, trả lời đúng 1 câu ngắn."}],
        )
        print(f"OK sau {time.time() - start:.1f}s ->", r.choices[0].message.content)
    except Exception as e:
        print(f"LỖI sau {time.time() - start:.1f}s ->", e)