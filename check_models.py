import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SOURCES = {
    "LM Studio": {
        "base_url": "http://localhost:1234/v1",
        "api_key": "lm-studio",
    },
    "Gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key": os.getenv("GEMINI_API_KEY", ""),
    },
}

for name, cfg in SOURCES.items():
    print(f"\n===== {name} =====")
    if name == "Gemini" and not cfg["api_key"]:
        print("Chưa đọc được GEMINI_API_KEY. Kiểm tra file .env (tên đúng là .env, không phải .env.txt).")
        continue
    try:
        client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
        for m in client.models.list():
            print(" -", m.id)
    except Exception as e:
        print("Lỗi:", e)