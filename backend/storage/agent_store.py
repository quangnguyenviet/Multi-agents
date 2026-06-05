# agent_store.py - Persist agents to JSON file
import os
import json
import threading
from typing import Optional

STORAGE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_FILE = os.path.join(STORAGE_DIR, "agents.json")

_write_lock = threading.Lock()

# Builtin seed data — matches App.jsx hardcoded values exactly
BUILTIN_AGENTS = {
    "auto_route": {
        "id": "auto_route",
        "name": "✨ Tự động định tuyến (Router)",
        "icon": "fa-route",
        "description": "Hệ thống tự động phân loại ý định người dùng và chuyển tiếp đến Agent xử lý phù hợp nhất trong LangGraph.",
        "welcome": "Xin chào! Tôi là **Router Tự động**. Hệ thống đang hoạt động ở chế độ phân phối thông minh. Bạn có thể hỏi bất kỳ câu hỏi nào về nhân sự, lương thưởng hoặc hệ thống, tôi sẽ tự động định tuyến đến Agent phù hợp nhất trong Graph!",
        "system_prompt": "",
        "is_builtin": True,
        "created_by": "System"
    },
    "hr_policies": {
        "id": "hr_policies",
        "name": "HR Policies Agent",
        "icon": "fa-users-gear",
        "description": "Giải đáp quy định, quy chế công ty, chế độ phép năm, bảo hiểm.",
        "welcome": "Chào bạn! Tôi là **HR Policies Agent**. Tôi chịu trách nhiệm giải đáp các thông tin chính thức liên quan đến: Quy chế công sở, Giờ giấc làm việc, và Ngày nghỉ phép.",
        "system_prompt": "",
        "is_builtin": True,
        "created_by": "System"
    },
    "salary_management": {
        "id": "salary_management",
        "name": "Salary Management Agent",
        "icon": "fa-wallet",
        "description": "Quản lý và tra cứu thông tin bảng lương, tính thưởng và báo cáo lương.",
        "welcome": "Xin chào! Tôi là **Salary Management Agent**. Tôi có thể hỗ trợ tra cứu lương của bạn, tính toán thưởng Tết và kết xuất báo cáo lương công ty dành cho Quản lý.",
        "system_prompt": "",
        "is_builtin": True,
        "created_by": "System"
    },
    "system_admin": {
        "id": "system_admin",
        "name": "System Admin Agent",
        "icon": "fa-server",
        "description": "Theo dõi và giám sát hiệu năng máy chủ, CPU, RAM và log hệ thống.",
        "welcome": "Kết nối hạ tầng Dell PowerEdge R750. Tôi là **System Admin Agent**, sẵn sàng hỗ trợ kiểm tra tài nguyên CPU, RAM, dung lượng SSD và đọc logs máy chủ.",
        "system_prompt": "",
        "is_builtin": True,
        "created_by": "System"
    },
    "user_management": {
        "id": "user_management",
        "name": "User Management Agent",
        "icon": "fa-user-gear",
        "description": "Quản lý người dùng, tài khoản demo và liên kết API cổng 8080.",
        "welcome": "Xin chào! Tôi là **User Management Agent**. Tôi quản lý danh sách người dùng hệ thống, tài khoản demo/test và các liên kết API cổng 8080.",
        "system_prompt": "",
        "is_builtin": True,
        "created_by": "System"
    }
}

# RBAC mapping — used by get_agents_for_user
ROLE_PERMISSIONS = {
    "employee": ["hr_policies", "salary_management"],
    "accountant": ["hr_policies", "salary_management", "user_management"],
    "admin": ["hr_policies", "salary_management", "system_admin", "user_management"]
}


def _init_agent_store():
    """Create agents.json with builtin seed data if file does not exist."""
    if not os.path.exists(AGENTS_FILE):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        with _write_lock:
            # Double-check after acquiring lock
            if not os.path.exists(AGENTS_FILE):
                _save_agents(BUILTIN_AGENTS.copy())
                print(f"📦 Initialized agent store with {len(BUILTIN_AGENTS)} builtin agents at {AGENTS_FILE}")


def _load_agents() -> dict:
    """Read and return the full agents dict from disk."""
    if not os.path.exists(AGENTS_FILE):
        _init_agent_store()
    with open(AGENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_agents(agents: dict):
    """Write the full agents dict atomically to disk."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    tmp_path = AGENTS_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, AGENTS_FILE)


# ---- Public API ----

def load_agents() -> dict:
    return _load_agents()


def get_agent(agent_id: str) -> Optional[dict]:
    agents = _load_agents()
    return agents.get(agent_id)


def add_agent(agent_data: dict) -> dict:
    agent_id = agent_data["id"]
    agents = _load_agents()
    if agent_id in agents:
        raise ValueError(f"Agent ID '{agent_id}' đã tồn tại")
    with _write_lock:
        agents = _load_agents()  # re-read under lock
        agents[agent_id] = {
            **agent_data,
            "is_builtin": False,
            "system_prompt": agent_data.get("system_prompt", ""),
            "created_by": agent_data.get("created_by", "Admin")
        }
        _save_agents(agents)
    return agents[agent_id]


def update_agent_prompt(agent_id: str, system_prompt: str) -> dict:
    agents = _load_agents()
    if agent_id not in agents:
        raise ValueError(f"Agent ID '{agent_id}' không tồn tại")
    with _write_lock:
        agents = _load_agents()
        agents[agent_id]["system_prompt"] = system_prompt
        _save_agents(agents)
    return agents[agent_id]


def delete_agent(agent_id: str):
    agents = _load_agents()
    if agent_id not in agents:
        raise ValueError(f"Agent ID '{agent_id}' không tồn tại")
    if agents[agent_id].get("is_builtin", False):
        raise ValueError(f"Không thể xóa builtin agent '{agent_id}'")
    with _write_lock:
        agents = _load_agents()
        if agent_id in agents and not agents[agent_id].get("is_builtin", False):
            del agents[agent_id]
            _save_agents(agents)


def get_agents_for_user(role: str) -> list:
    """Return agents accessible for a given role (RBAC filtered)."""
    agents = _load_agents()
    allowed_ids = ROLE_PERMISSIONS.get(role, ["hr_policies"])
    result = []
    for aid, ainfo in agents.items():
        if aid == "auto_route":
            continue  # internal router, not user-facing
        result.append({
            "id": aid,
            "name": ainfo["name"],
            "description": ainfo["description"],
            "icon": ainfo["icon"],
            "welcome": ainfo.get("welcome", ""),
            "is_allowed": aid in allowed_ids
        })
    return result


# Auto-init on import
_init_agent_store()
