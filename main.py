import os
from typing import TypedDict, Literal, Any
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()


# === 1. ĐỊNH NGHĨA STATE (Trạng thái duy trì xuyên suốt đồ thị đa Agent) ===
class MultiAgentState(TypedDict):
    user_id: str
    user_role: Literal["employee", "accountant", "admin"]
    user_name: str
    query: str
    target_agent: Literal["hr_policies", "salary_management", "system_admin", "unknown"]
    access_granted: bool
    agent_response: str


# === 2. GIẢ LẬP CƠ SỞ DỮ LIỆU BẢO MẬT ===
SALARY_DB = {
    "Nguyen Van A": {"salary": 15000000, "role": "employee"},
    "Tran Thi B": {"salary": 18000000, "role": "employee"},
    "Le Van C": {"salary": 22000000, "role": "accountant"},
    "Nguyen Admin": {"salary": 30000000, "role": "admin"}
}

EMPLOYEE_INFO = {
    "emp_001": {"name": "Nguyen Van A", "role": "employee"},
    "emp_002": {"name": "Tran Thi B", "role": "employee"},
    "acc_001": {"name": "Le Van C", "role": "accountant"},
    "adm_001": {"name": "Nguyen Admin", "role": "admin"}
}


# === 3. HÀM LẤY THÔNG TIN USER ===
def get_user_info(user_id: str) -> dict:
    return EMPLOYEE_INFO.get(user_id, {"name": "Unknown", "role": "employee"})


# === 4. NODE ĐỊNH TUYẾN & KIỂM SOÁT TRUY CẬP (Router & RBAC Node) ===
def router_node(state: MultiAgentState) -> MultiAgentState:
    """
    Node đầu tiên: Sử dụng LLM phân tích ý định câu hỏi để định tuyến tới Agent phù hợp
    và kiểm tra quyền truy cập dựa trên vai trò (Router-Level Security).
    """
    query = state["query"]
    user_role = state["user_role"]
    user_name = state["user_name"]
    
    # Khởi tạo mô hình định tuyến
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        temperature=0
    )
    
    system_prompt = (
        "Bạn là bộ định tuyến AI phân loại yêu cầu người dùng vào các Agent chuyên biệt:\n"
        "- 'hr_policies': các câu hỏi về quy định, quy chế công ty, chế độ phép năm, bảo hiểm, nội quy phúc lợi.\n"
        "- 'salary_management': các câu hỏi về tra cứu bảng lương, lương thưởng, chi tiết lương của cá nhân hoặc người khác.\n"
        "- 'system_admin': các câu hỏi về vận hành, trạng thái máy chủ (CPU, RAM, logs, ổ cứng).\n"
        "- 'unknown': câu hỏi không thuộc các lĩnh vực trên hoặc chỉ là chào hỏi bình thường.\n\n"
        "Yêu cầu: CHỈ trả về đúng 1 trong 4 từ khóa sau: 'hr_policies', 'salary_management', 'system_admin', 'unknown'. "
        "Không thêm bất kỳ chữ nào khác, không viết hoa, không dấu câu."
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Phân loại câu hỏi sau: '{query}'")
    ]
    
    # Gọi LLM để định tuyến
    try:
        response = llm.invoke(messages)
        target_agent = response.content.strip().lower().replace("'", "").replace('"', '')
    except Exception as e:
        print(f"⚠️ Lỗi gọi LLM phân loại định tuyến: {e}. Sử dụng mặc định 'unknown'")
        target_agent = "unknown"
        
    if target_agent not in ["hr_policies", "salary_management", "system_admin", "unknown"]:
        target_agent = "unknown"
        
    state["target_agent"] = target_agent
    
    # === BẢN ĐỒ PHÂN QUYỀN TRUY CẬP (ROUTER-LEVEL RBAC) ===
    # employee: được vào HR Policies và Salary Management (sẽ được kiểm soát chi tiết tiếp ở Agent-Level)
    # accountant: được vào HR Policies và Salary Management
    # admin: được vào tất cả mọi Agent bao gồm cả System Admin
    role_permissions = {
        "employee": ["hr_policies", "salary_management"],
        "accountant": ["hr_policies", "salary_management"],
        "admin": ["hr_policies", "salary_management", "system_admin"]
    }
    
    allowed_agents = role_permissions.get(user_role, ["hr_policies"])
    
    # Định tuyến mặc định/chào hỏi không cần check quyền đặc biệt
    if target_agent == "unknown":
        state["access_granted"] = True
    elif target_agent in allowed_agents:
        state["access_granted"] = True
        print(f"✅ [ROUTER] {user_role.upper()} {user_name} được chuyển tiếp đến Agent: {target_agent}")
    else:
        # Bị chặn ngay từ tầng Router
        state["access_granted"] = False
        print(f"❌ [ROUTER] {user_role.upper()} {user_name} BỊ CHẶN truy cập vào Agent: {target_agent}")
        state["agent_response"] = (
            f"❌ TRUY CẬP BỊ TỪ CHỐI!\n"
            f"Vai trò [{user_role.upper()}] của bạn không có quyền truy cập vào Agent Quản Trị Hệ Thống ({target_agent}). "
            f"Vui lòng liên hệ Quản trị viên để cấp quyền."
        )
        
    return state


# === 5. NODE AGENT 1: QUY CHẾ & PHÚC LỢI (HR Agent) ===
def hr_policies_node(state: MultiAgentState) -> MultiAgentState:
    """
    Agent chuyên trách trả lời chính sách, nội quy công ty.
    Tất cả mọi vai trò (Employee, Accountant, Admin) đều có quyền xem.
    """
    query = state["query"]
    
    # Mock tài liệu HR quy chế của công ty
    hr_documents = (
        "QUY CHẾ NỘI BỘ VÀ CHẾ ĐỘ PHÚC LỢI CÔNG TY:\n"
        "1. Thời gian làm việc: Từ 8:00 đến 17:30 hằng ngày, từ thứ Hai đến thứ Sáu. Nghỉ trưa từ 12:00 đến 13:30.\n"
        "2. Nghỉ phép năm: Nhân viên chính thức có 12 ngày phép năm hưởng nguyên lương. Cứ mỗi 5 năm thâm niên được thêm 1 ngày phép.\n"
        "3. Chế độ bảo hiểm: BHXH, BHYT, BHTN được đóng 100% dựa trên mức lương thực nhận hợp đồng.\n"
        "4. Lễ tết & Thưởng: Thưởng Quốc khánh (2/9), Giải phóng (30/4) là 1.000.000 VND/người. Thưởng tết Nguyên Đán lương tháng 13 dựa trên đánh giá KPI năm.\n"
        "5. Quy định trang phục: Trang phục lịch sự công sở vào thứ Hai đến thứ Năm. Thứ Sáu được phép mặc trang phục tự do."
    )
    
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        temperature=0.2
    )
    
    messages = [
        SystemMessage(content=(
            "Bạn là HR Agent chuyên trách giải đáp thắc mắc nội quy, quy chế nhân sự của công ty.\n"
            "Dưới đây là thông tin tài liệu chính thức:\n"
            f"=== TÀI LIỆU HR ===\n{hr_documents}\n==================\n"
            "Hãy trả lời câu hỏi dựa trên tài liệu trên một cách thân thiện, chính xác. "
            "Nếu thông tin không có trong tài liệu, hãy nhẹ nhàng báo rằng thông tin này chưa được cập nhật."
        )),
        HumanMessage(content=query)
    ]
    
    response = llm.invoke(messages)
    state["agent_response"] = response.content
    return state


# === 6. NODE AGENT 2: QUẢN LÝ LƯƠNG (Salary Agent - Tích hợp Bảo mật tầng sâu) ===
def salary_management_node(state: MultiAgentState) -> MultiAgentState:
    """
    Agent quản lý tiền lương.
    Tích hợp bảo mật tầng sâu (Agent-Level Security):
    - Employee: Chỉ được xem lương của CHÍNH MÌNH. Nếu hỏi lương người khác sẽ bị từ chối.
    - Accountant & Admin: Được quyền xem lương của tất cả nhân viên.
    """
    query = state["query"]
    user_role = state["user_role"]
    user_name = state["user_name"]
    query_lower = query.lower()
    
    # 1. Phát hiện mục đích truy vấn
    asking_all = any(k in query_lower for k in ["tất cả", "mọi người", "toàn bộ", "danh sách", "ai"])
    asking_others = False
    
    # Kiểm tra xem có đang hỏi tên của một người khác trong DB không
    target_person = None
    for name in SALARY_DB.keys():
        if name.lower() != user_name.lower() and name.lower() in query_lower:
            asking_others = True
            target_person = name
            break

    # 2. Áp dụng logic bảo mật Agent-Level (Kiểm soát chi tiết dữ liệu đầu ra)
    context = ""
    denied = False
    
    if user_role == "employee":
        if asking_all or asking_others:
            denied = True
            state["agent_response"] = (
                f"❌ TRUY CẬP BỊ TỪ CHỐI TẠI AGENT LƯƠNG!\n"
                f"Tài khoản Nhân viên [{user_name}] của bạn chỉ được phép truy vấn lương cá nhân. "
                f"Bạn không có quyền xem thông tin lương của người khác."
            )
        else:
            # Chỉ lấy đúng dữ liệu lương của bản thân
            salary_data = SALARY_DB.get(user_name, {})
            context = f"Lương của bạn ({user_name}) là: {salary_data.get('salary', 0):,} VND"
            
    elif user_role in ["accountant", "admin"]:
        # Accountant & Admin được quyền truy cập mọi thông tin
        if asking_all:
            list_salary = [f"- {name}: {data['salary']:,} VND ({data['role'].upper()})" for name, data in SALARY_DB.items()]
            context = "DANH SÁCH BẢNG LƯƠNG TOÀN CÔNG TY:\n" + "\n".join(list_salary)
        elif asking_others and target_person:
            salary_data = SALARY_DB.get(target_person, {})
            context = f"Lương của nhân viên {target_person} ({salary_data.get('role').upper()}) là: {salary_data.get('salary', 0):,} VND"
        else:
            # Mặc định hỏi lương cá nhân của họ
            salary_data = SALARY_DB.get(user_name, {})
            context = f"Lương của bạn ({user_name}) là: {salary_data.get('salary', 0):,} VND"
            
    if denied:
        return state

    # 3. Gọi LLM để định dạng câu trả lời bảo mật
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        temperature=0.1
    )
    
    messages = [
        SystemMessage(content=(
            "Bạn là Agent quản lý lương bảo mật của công ty.\n"
            "Hãy trả lời câu hỏi dựa trên dữ liệu hệ thống được cung cấp dưới đây một cách lịch sự, chính xác. "
            "Trình bày các con số và danh sách một cách trực quan, khoa học bằng Markdown.\n"
            f"=== DỮ LIỆU ĐƯỢC PHÉP TRUY CẬP ===\n{context}\n=================================="
        )),
        HumanMessage(content=query)
    ]
    
    response = llm.invoke(messages)
    state["agent_response"] = response.content
    return state


# === 7. NODE AGENT 3: QUẢN TRỊ HỆ THỐNG (System Admin Agent) ===
def system_admin_node(state: MultiAgentState) -> MultiAgentState:
    """
    Agent quản trị hạ tầng kỹ thuật.
    Chỉ có tài khoản 'admin' mới được phép truy cập (được bảo vệ từ Router-level).
    """
    query = state["query"]
    
    # Mock dữ liệu trạng thái máy chủ bảo mật
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
    
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        temperature=0.1
    )
    
    messages = [
        SystemMessage(content=(
            "Bạn là System Admin Agent chuyên trách theo dõi hạ tầng hệ thống của công ty.\n"
            "Dưới đây là thông số thời gian thực thu thập được từ máy chủ chính:\n"
            f"=== THÔNG SỐ HỆ THỐNG ===\n{server_metrics}\n=========================\n"
            "Hãy tổng hợp và giải đáp thắc mắc cho kỹ sư/quản trị viên một cách chuyên nghiệp, chính xác. "
            "Sử dụng bảng biểu và highlight nếu cần để báo cáo trực quan."
        )),
        HumanMessage(content=query)
    ]
    
    response = llm.invoke(messages)
    state["agent_response"] = response.content
    return state


# === 8. NODE PHỤ: XỬ LÝ CHÀO HỎI & CÂU HỎI CHUNG (General Handler) ===
def general_handler_node(state: MultiAgentState) -> MultiAgentState:
    """
    Xử lý các câu hỏi nằm ngoài phạm vi hoặc chào hỏi thông thường.
    Hướng dẫn người dùng các chức năng phù hợp theo vai trò của họ.
    """
    query = state["query"]
    user_name = state["user_name"]
    user_role = state["user_role"]
    
    # Hướng dẫn tuỳ chỉnh theo vai trò
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
            "- Hỏi và quản lý lương của tất cả mọi người (ví dụ: 'Cho tôi xem danh sách lương công ty', 'Lương của Nguyen Van A bao nhiêu?') tại Salary Agent."
        )
    elif user_role == "admin":
        guide = (
            "Với vai trò Quản trị viên (Admin), bạn có quyền truy cập toàn bộ hệ thống:\n"
            "- Hỏi về quy chế công ty (HR Agent).\n"
            "- Quản lý bảng lương của toàn bộ nhân viên (Salary Agent).\n"
            "- Kiểm tra và quản trị hạ tầng kỹ thuật máy chủ (ví dụ: 'Xem trạng thái CPU và RAM', 'Kiểm tra lỗi server hôm nay') tại System Admin Agent."
        )
        
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
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


# === 9. HÀM ĐỊNH TUYẾN TRONG ĐỒ THỊ LANGGRAPH ===
def route_to_agent(state: MultiAgentState) -> str:
    """
    Hàm phân phối điều kiện để quyết định Node tiếp theo dựa trên kết quả của Router Node
    """
    if not state["access_granted"]:
        return "end"
        
    target = state["target_agent"]
    if target == "hr_policies":
        return "hr_policies"
    elif target == "salary_management":
        return "salary_management"
    elif target == "system_admin":
        return "system_admin"
    else:
        return "general_handler"


# === 10. XÂY DỰNG ĐỒ THỊ ĐA AGENT PHÂN QUYỀN ===
def build_multi_agent_system():
    workflow = StateGraph(MultiAgentState)
    
    # Đăng ký các Node
    workflow.add_node("router", router_node)
    workflow.add_node("hr_policies", hr_policies_node)
    workflow.add_node("salary_management", salary_management_node)
    workflow.add_node("system_admin", system_admin_node)
    workflow.add_node("general_handler", general_handler_node)
    
    # Thiết lập điểm vào chính
    workflow.set_entry_point("router")
    
    # Thiết lập các liên kết điều kiện từ Router Node
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "hr_policies": "hr_policies",
            "salary_management": "salary_management",
            "system_admin": "system_admin",
            "general_handler": "general_handler",
            "end": END
        }
    )
    
    # Liên kết các Agent về điểm kết thúc END
    workflow.add_edge("hr_policies", END)
    workflow.add_edge("salary_management", END)
    workflow.add_edge("system_admin", END)
    workflow.add_edge("general_handler", END)
    
    return workflow.compile()


# === 11. HÀM GIAO DIỆN CHAT TƯƠNG TÁC QUA TERMINAL ===
def run_interactive():
    chatbot = build_multi_agent_system()
    print("\n" + "=" * 65)
    print("   🌐 HỆ THỐNG ĐA AGENT ĐỊNH TUYẾN & PHÂN QUYỀN TỰ ĐỘNG (RBAC) 🌐")
    print("=" * 65)
    
    print("\nDanh sách tài khoản giả lập trong hệ thống:")
    for uid, info in EMPLOYEE_INFO.items():
        print(f"  - ID: {uid:<8} | Tên: {info['name']:<15} | Vai trò: {info['role'].upper()}")
    
    # Đăng nhập
    user_id = ""
    while not user_id:
        uid_input = input("\n👉 Nhập User ID của bạn để đăng nhập (ví dụ: emp_001, acc_001, adm_001): ").strip()
        if uid_input in EMPLOYEE_INFO:
            user_id = uid_input
        else:
            print("❌ ID tài khoản không tồn tại. Vui lòng thử lại!")

    user_info = get_user_info(user_id)
    name = user_info["name"]
    role = user_info["role"]

    print(f"\n✅ ĐĂNG NHẬP THÀNH CÔNG!")
    print(f"👤 Người dùng: {name}")
    print(f"🔑 Vai trò: {role.upper()}")
    print("-" * 65)
    print("Bắt đầu đặt câu hỏi cho hệ thống đa Agent.")
    print("Gõ 'exit' hoặc 'quit' để kết thúc.")
    print("-" * 65)

    while True:
        try:
            query = input(f"\n👤 {name} ({role.upper()}) > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                print("\n👋 Đã thoát phiên làm việc. Tạm biệt!")
                break

            # Thực thi đồ thị
            result = chatbot.invoke({
                "user_id": user_id,
                "user_role": role,
                "user_name": name,
                "query": query,
                "target_agent": "unknown",
                "access_granted": False,
                "agent_response": ""
            })
            
            print(f"\n🤖 Agent Trả Lời:\n{result['agent_response']}")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n👋 Đã thoát phiên làm việc. Tạm biệt!")
            break
        except Exception as e:
            print(f"\n❌ Đã xảy ra lỗi hệ thống: {e}")


if __name__ == "__main__":
    run_interactive()