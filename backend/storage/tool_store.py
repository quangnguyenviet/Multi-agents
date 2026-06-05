# tool_store.py - Persist tools to JSON file
import os
import json
import threading
from typing import Optional

STORAGE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_FILE = os.path.join(STORAGE_DIR, "tools.json")

_write_lock = threading.Lock()

# Seed tools — matches App.jsx hardcoded initialTools exactly
SEED_TOOLS = [
    {
        "id": "get_company_employee_list",
        "name": "get_company_employee_list",
        "icon": "fa-address-book",
        "description": "Truy xuất danh sách toàn bộ nhân sự công ty bao gồm Mã nhân viên, Họ tên, Phòng ban và Vai trò.",
        "agent": "system_admin",
        "category": "Database Query",
        "active": True,
        "created_by": "System"
    },
    {
        "id": "hr_policy_retriever",
        "name": "hr_policy_retriever",
        "icon": "fa-file-shield",
        "description": "Tìm kiếm ngữ cảnh liên quan đến chính sách nhân sự trong cơ sở dữ liệu Vector (Chuyên dùng cho RAG).",
        "agent": "hr_policies",
        "category": "Vector Search",
        "active": True,
        "created_by": "System"
    },
    {
        "id": "salary_calculator",
        "name": "salary_calculator",
        "icon": "fa-calculator",
        "description": "Tính toán tổng thu nhập, khấu trừ bảo hiểm xã hội và thuế TNCN theo công thức lương mới nhất.",
        "agent": "salary_management",
        "category": "Math/Logic",
        "active": True,
        "created_by": "System"
    }
]


def _init_tool_store():
    """Create tools.json with seed data if file does not exist."""
    if not os.path.exists(TOOLS_FILE):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        with _write_lock:
            if not os.path.exists(TOOLS_FILE):
                _save_tools(SEED_TOOLS.copy())
                print(f"📦 Initialized tool store with {len(SEED_TOOLS)} seed tools at {TOOLS_FILE}")


def _load_tools() -> list:
    """Read and return the tools list from disk."""
    if not os.path.exists(TOOLS_FILE):
        _init_tool_store()
    with open(TOOLS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_tools(tools: list):
    """Write the tools list atomically to disk."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    tmp_path = TOOLS_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(tools, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, TOOLS_FILE)


# ---- Public API ----

def load_tools() -> list:
    return _load_tools()


def get_tool(tool_id: str) -> Optional[dict]:
    tools = _load_tools()
    for t in tools:
        if t["id"] == tool_id:
            return t
    return None


def add_tool(tool_data: dict) -> dict:
    tool_id = tool_data["id"]
    existing = get_tool(tool_id)
    if existing:
        raise ValueError(f"Tool ID '{tool_id}' đã tồn tại")
    with _write_lock:
        tools = _load_tools()
        new_tool = {
            "id": tool_id,
            "name": tool_data.get("name", tool_id),
            "icon": tool_data.get("icon", "fa-globe"),
            "description": tool_data.get("description", ""),
            "agent": tool_data.get("agent", "system_admin"),
            "category": tool_data.get("category", "Database Query"),
            "active": True,
            "created_by": tool_data.get("created_by", "Admin")
        }
        tools.append(new_tool)
        _save_tools(tools)
    return new_tool


def update_tool(tool_id: str, updates: dict) -> dict:
    with _write_lock:
        tools = _load_tools()
        for t in tools:
            if t["id"] == tool_id:
                for key, value in updates.items():
                    if key in t and value is not None:
                        t[key] = value
                _save_tools(tools)
                return t
    raise ValueError(f"Tool ID '{tool_id}' không tồn tại")


def delete_tool(tool_id: str):
    with _write_lock:
        tools = _load_tools()
        filtered = [t for t in tools if t["id"] != tool_id]
        if len(filtered) == len(tools):
            raise ValueError(f"Tool ID '{tool_id}' không tồn tại")
        _save_tools(filtered)


# Auto-init on import
_init_tool_store()
