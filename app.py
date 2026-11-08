import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from agent import run_agent

load_dotenv()

# Mỗi nguồn nhớ tên model riêng
PROVIDERS = {
    "Gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "model": "gemini-3.1-flash-lite",
    },
    "LM Studio (local)": {
        "base_url": "http://localhost:1234/v1",
        "api_key": "lm-studio",
        "model": "qwen/qwen3-4b-2507",
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


def show_events(events):
    """Hiển thị các lần AI đã gọi tool."""
    for e in events:
        with st.expander(f"🔧 Đã gọi tool: {e['tool']}"):
            st.write("**Tham số:**")
            st.json(e["args"])
            st.write("**Kết quả:**")
            st.code(e["result"])


st.set_page_config(page_title="AI cá nhân", page_icon="🤖")
st.title("🤖 AI cá nhân")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Cài đặt")
    provider_name = st.selectbox("Nguồn model", list(PROVIDERS.keys()))
    cfg = PROVIDERS[provider_name]
    # key theo nguồn để đổi nguồn thì tên model tự đổi theo
    model = st.text_input("Tên model", value=cfg["model"], key=f"model_{provider_name}")
    st.caption("AI có thể đọc/ghi file trong thư mục `workspace/`.")
    if st.button("🗑️ Xóa lịch sử chat"):
        st.session_state.history = []
        save_history([])
        st.rerun()

# ---------- State ----------
if "history" not in st.session_state:
    st.session_state.history = load_history()

profile = PROFILE_FILE.read_text(encoding="utf-8") if PROFILE_FILE.exists() else ""
system_prompt = f"""Bạn là trợ lý cá nhân của tôi. Trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu.
Bạn có các tool để xem, đọc và ghi file trong thư mục workspace. Chỉ dùng tool khi thật sự cần.
Trước khi ghi đè một file đã có, hãy đọc nó trước. Sau khi dùng tool, báo lại ngắn gọn bạn đã làm gì.
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

    with st.chat_message("assistant"):
        try:
            with st.spinner("AI đang suy nghĩ..."):
                answer, events = run_agent(
                    client, model, system_prompt, st.session_state.history[-30:]
                )
            show_events(events)
            st.markdown(answer)
        except Exception as e:
            answer = f"⚠️ Lỗi: {e}"
            st.markdown(answer)

    # Chỉ lưu lời nói của bạn và câu trả lời cuối vào lịch sử
    st.session_state.history.append({"role": "assistant", "content": answer})
    save_history(st.session_state.history)