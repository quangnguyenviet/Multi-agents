from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings
from .workflow_state import MultiAgentState

# === NODE ĐỊNH TUYẾN & KIỂM SOÁT TRUY CẬP (Router & RBAC Node) ===
def router_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    user_role = state["user_role"]
    user_name = state["user_name"]
    
    # Respect the pre-selected target_agent if it's a valid agent ID
    target_agent = state.get("target_agent", "unknown")
    
    if target_agent not in ["hr_policies", "salary_management", "system_admin", "user_management"]:
        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=0
        )
        
        system_prompt = (
            "Bạn là bộ định tuyến AI phân loại yêu cầu người dùng vào các Agent chuyên biệt:\n"
            "- 'hr_policies': các câu hỏi về quy định, quy chế công ty, chế độ phép năm, bảo hiểm, nội quy phúc lợi.\n"
            "- 'salary_management': các câu hỏi về tra cứu bảng lương, lương thưởng, chi tiết lương của cá nhân hoặc người khác.\n"
            "- 'system_admin': các câu hỏi về vận hành, trạng thái máy chủ (CPU, RAM, logs, ổ cứng).\n"
            "- 'user_management': các câu hỏi về quản lý người dùng, tài khoản tester, danh sách user demo, thông tin liên hệ user cổng 8080.\n"
            "- 'unknown': câu hỏi không thuộc các lĩnh vực trên hoặc chỉ là chào hỏi bình thường.\n\n"
            "Yêu cầu: CHỈ trả về đúng 1 trong 5 từ khóa sau: 'hr_policies', 'salary_management', 'system_admin', 'user_management', 'unknown'. "
            "Không thêm bất kỳ chữ nào khác, không viết hoa, không dấu câu."
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Phân loại câu hỏi sau: '{query}'")
        ]
        
        try:
            response = llm.invoke(messages)
            target_agent = response.content.strip().lower().replace("'", "").replace('"', '')
        except Exception as e:
            print(f"⚠️ Lỗi định tuyến: {e}. Dùng mặc định 'unknown'")
            target_agent = "unknown"
            
        if target_agent not in ["hr_policies", "salary_management", "system_admin", "user_management", "unknown"]:
            target_agent = "unknown"
            
    state["target_agent"] = target_agent
    
    # Bản đồ quyền hạn (RBAC)
    role_permissions = {
        "employee": ["hr_policies", "salary_management"],
        "accountant": ["hr_policies", "salary_management", "user_management"],
        "admin": ["hr_policies", "salary_management", "system_admin", "user_management"]
    }
    
    allowed_agents = role_permissions.get(user_role, ["hr_policies"])
    
    if target_agent == "unknown":
        state["access_granted"] = True
    elif target_agent in allowed_agents:
        state["access_granted"] = True
        print(f"✅ [ROUTER] {user_role.upper()} {user_name} được chuyển tiếp đến Agent: {target_agent}")
    else:
        state["access_granted"] = False
        print(f"❌ [ROUTER] {user_role.upper()} {user_name} BỊ CHẶN truy cập vào Agent: {target_agent}")
        state["agent_response"] = (
            f"❌ TRUY CẬP BỊ TỪ CHỐI!\n"
            f"Vai trò [{user_role.upper()}] của bạn không có quyền truy cập vào Agent Quản Trị Hệ Thống ({target_agent}). "
            f"Vui lòng liên hệ Quản trị viên để cấp quyền."
        )
        
    return state

# === HÀM ĐỊNH TUYẾN TRONG ĐỒ THỊ LANGGRAPH ===
def route_to_agent(state: MultiAgentState) -> str:
    if not state["access_granted"]:
        return "end"
        
    target = state["target_agent"]
    if target == "hr_policies":
        return "hr_policies"
    elif target == "salary_management":
        return "salary_management"
    elif target == "system_admin":
        return "system_admin"
    elif target == "user_management":
        return "user_management"
    else:
        return "general_handler"
