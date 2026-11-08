from pathlib import Path

# Thư mục AI được phép làm việc. Mọi file AI đọc/ghi đều nằm trong đây.
WORKSPACE = Path("workspace").resolve()
WORKSPACE.mkdir(exist_ok=True)


def _safe_path(rel_path: str) -> Path:
    """Chuyển đường dẫn tương đối thành đường dẫn thật, và CHẶN việc thoát ra ngoài workspace."""
    p = (WORKSPACE / rel_path).resolve()
    if not p.is_relative_to(WORKSPACE):
        raise ValueError("Đường dẫn nằm ngoài thư mục workspace, không được phép.")
    return p


def list_files(path: str = ".") -> str:
    p = _safe_path(path)
    if not p.exists():
        return f"Không tìm thấy: {path}"
    items = sorted(p.iterdir())
    if not items:
        return "(thư mục trống)"
    return "\n".join(("[thư mục] " if i.is_dir() else "[file] ") + i.name for i in items)


def read_file(path: str) -> str:
    p = _safe_path(path)
    if not p.is_file():
        return f"Không tìm thấy file: {path}"
    return p.read_text(encoding="utf-8")[:10000]  # giới hạn 10.000 ký tự


def write_file(path: str, content: str) -> str:
    p = _safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Đã ghi {len(content)} ký tự vào {path}"


# Hàm nào ứng với tên tool nào
FUNCS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
}

# Mô tả tool để model biết khi nào nên gọi (chuẩn OpenAI, dùng được cho Gemini và LM Studio)
TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Liệt kê file và thư mục trong workspace. Dùng khi cần biết có những file nào.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Thư mục con cần xem, mặc định là '.'"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Đọc nội dung một file text trong workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Đường dẫn file, ví dụ 'ghi_chu.md'"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Tạo mới hoặc ghi đè một file text trong workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Đường dẫn file, ví dụ 'todo.md'"},
                    "content": {"type": "string", "description": "Toàn bộ nội dung file"},
                },
                "required": ["path", "content"],
            },
        },
    },
]


def run_tool(name: str, args: dict) -> str:
    """Chạy tool theo tên. Bắt mọi lỗi để trả lại cho AI thay vì làm sập app."""
    if name not in FUNCS:
        return f"Tool không tồn tại: {name}"
    try:
        return str(FUNCS[name](**args))
    except Exception as e:
        return f"Lỗi khi chạy tool {name}: {e}"