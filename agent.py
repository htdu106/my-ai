import json

from tools import TOOLS_SPEC, run_tool

MAX_STEPS = 8  # giới hạn số vòng, tránh AI lặp vô hạn và tốn tiền


def run_agent(client, model, system_prompt, history):
    """
    Vòng lặp agent:
      1. Gửi hội thoại + danh sách tool cho model.
      2. Nếu model muốn gọi tool -> mình chạy tool, gửi kết quả lại, quay về bước 1.
      3. Nếu model trả lời bằng chữ thường -> xong.
    Trả về (câu trả lời cuối, danh sách các lần gọi tool để hiển thị).
    """
    messages = [{"role": "system", "content": system_prompt}] + history
    events = []

    for _ in range(MAX_STEPS):
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS_SPEC,
        )
        msg = resp.choices[0].message

        # Không gọi tool -> đây là câu trả lời cuối
        if not msg.tool_calls:
            return msg.content or "", events

        # Có gọi tool -> lưu lại lượt nói của model (giữ nguyên mọi trường model gửi về)
        messages.append(msg.model_dump(exclude_none=True))

        for call in msg.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            result = run_tool(name, args)
            events.append({"tool": name, "args": args, "result": result})

            # Gửi kết quả tool về cho model
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": name,
                    "content": result,
                }
            )

    return "⚠️ Dừng lại vì AI gọi tool quá nhiều lần liên tiếp.", events