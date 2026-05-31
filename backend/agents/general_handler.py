from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings
from .workflow_state import MultiAgentState

# === NODE PHỤ: XỬ LÝ CHÀO HỎI & CÂU HỎI CHUNG (General Handler) ===
def general_handler_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    user_name = state["user_name"]
    user_role = state["user_role"]
    
    guide = ""
    if user_role == "employee":
        guide = (
            "Với vai trò Nhân viên, bạn có quyền:\n"
            "- Hỏi về chế độ, quy định công ty (ví dụ: 'Quy định nghỉ phép năm', 'Giờ làm việc thế nào?') tại HR Agent.\n"
            "- Hỏi về thông tin lương cá nhân của bạn (ví dụ: 'Lương tháng này của tôi bao nhiêu?') tại Salary Agent."
        )
    elif user_role == "accountant":
        guide = (
            "Với vai trò Kế toán, bạn có quyền:\n"
            "- Hỏi về chế độ, quy định công ty tại HR Agent.\n"
            "- Hỏi và quản lý lương của tất cả mọi người (ví dụ: 'Cho tôi xem danh sách lương công ty') tại Salary Agent."
        )
    elif user_role == "admin":
        guide = (
            "Với vai trò Quản trị viên (Admin), bạn có quyền truy cập toàn bộ hệ thống:\n"
            "- Hỏi về quy chế công ty (HR Agent).\n"
            "- Quản lý bảng lương của toàn bộ nhân viên (Salary Agent).\n"
            "- Kiểm tra và quản trị hạ tầng kỹ thuật máy chủ (ví dụ: 'Xem trạng thái CPU và RAM') tại System Admin Agent."
        )
        
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        base_url=settings.LLM_BASE_URL,
        temperature=0.5
    )
    
    messages = [
        SystemMessage(content=(
            "Bạn là trợ lý ảo hỗ trợ nội bộ thân thiện. Nhiệm vụ của bạn là chào đón người dùng, trả lời các "
            "câu hỏi xã giao bình thường và hướng dẫn họ các chức năng mà họ có quyền truy cập.\n"
            f"Thông tin người dùng hiện tại:\n- Tên: {user_name}\n- Vai trò: {user_role.upper()}\n\n"
            f"Hãy tích hợp hướng dẫn sử dụng sau vào câu trả lời của bạn một cách khéo léo:\n{guide}"
        )),
        HumanMessage(content=query)
    ]
    
    response = llm.invoke(messages)
    state["agent_response"] = response.content
    return state
