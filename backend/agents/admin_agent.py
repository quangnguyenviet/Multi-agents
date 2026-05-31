from .workflow_state import MultiAgentState
from .instances import system_admin_agent_with_skills

# === NODE AGENT 3: QUẢN TRỊ HỆ THỐNG (System Admin Agent) ===
async def system_admin_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    user_role = state["user_role"]
    user_name = state["user_name"]
    
    server_metrics = (
        "TRẠNG THÁI HẠ TẦNG KỸ THUẬT HỆ THỐNG:\n"
        "- Thiết bị: Dell PowerEdge R750 (2x Intel Xeon Gold 6330, 256GB RAM DDR4)\n"
        "- Trạng thái CPU: Đang tải 32% (Nhiệt độ trung bình 65°C - Ổn định)\n"
        "- Trạng thái RAM: Đang sử dụng 87.4 GB / 256 GB (34.1%)\n"
        "- Dung lượng ổ cứng NVMe SSD RAID-10: Trống 2.4 TB / 4.0 TB\n"
        "- Các dịch vụ đang chạy:\n"
        "  + Web Application (Nginx v1.25): RUNNING (Uptime: 142 ngày)\n"
        "  + Database Master (PostgreSQL v16): RUNNING (Uptime: 89 ngày)\n"
        "  + Redis Session Store: RUNNING (Uptime: 12 ngày)\n"
        "  + LangGraph Agentic Daemon: RUNNING (Uptime: 24 ngày, Active workers: 8)\n"
        "- Nhật ký lỗi hệ thống mới nhất:\n"
        "  + [2026-05-27 08:12:44] WARN: Redis memory usage exceeded 80% threshold. Cache cleared automatically.\n"
        "  + [2026-05-27 10:45:12] INFO: SSL certificate successfully renewed for api.company.com.\n"
        "  + [2026-05-27 12:30:00] INFO: Daily database backup completed successfully (Size: 14.2 GB)."
    )
    
    context = {
        "server_metrics": server_metrics,
        "user_name": user_name,
        "user_role": user_role
    }
    
    response = await system_admin_agent_with_skills.process(query, user_role, context)
    state["agent_response"] = response
    return state
