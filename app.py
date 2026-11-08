import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROVIDERS = {
    "LM Studio (local)": {
        "base_url": "http://localhost:1234/v1",
        "api_key": "lm-studio",
        "model": "qwen/qwen3-4b-2507",  # đổi đúng tên model bạn đã load
    },
    "Gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "model": "gemini-3.1-flash-lite",
    },
}

HISTORY_FILE = Path("history.json")
PROFILE_FILE = Path("profile.md")


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return []


def save_history(history):
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )


st.set_page_config(page_title="AI cá nhân", page_icon="🤖")
st.title("🤖 AI cá nhân")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Cài đặt")
    provider_name = st.selectbox("Nguồn model", list(PROVIDERS.keys()))
    cfg = PROVIDERS[provider_name]
    model = st.text_input("Tên model", value=cfg["model"])
    if st.button("🗑️ Xóa lịch sử chat"):
        st.session_state.history = []
        save_history([])
        st.rerun()

# ---------- State ----------
if "history" not in st.session_state:
    st.session_state.history = load_history()

profile = PROFILE_FILE.read_text(encoding="utf-8") if PROFILE_FILE.exists() else ""
system_prompt = f"""Bạn là trợ lý cá nhân của tôi. Trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu.
Thông tin về tôi:
{profile}"""

# ---------- Hiển thị lịch sử ----------
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Nhập tin nhắn ----------
if prompt := st.chat_input("Nhắn gì đó cho AI..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])

    def stream_answer():
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_prompt}]
                + st.session_state.history[-30:],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"⚠️ Lỗi: {e}\n\nKiểm tra: server LM Studio đã bật chưa? API key và tên model đúng chưa?"

    with st.chat_message("assistant"):
        answer = st.write_stream(stream_answer())

    st.session_state.history.append({"role": "assistant", "content": answer})
    save_history(st.session_state.history)