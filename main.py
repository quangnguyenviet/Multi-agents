# main.py - Phiên bản nâng cấp với Skill System
import os
import asyncio
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()
from skills.registry import SkillRegistry
from skills.factory import SkillFactory
from skills.builtin.salary_skills import all_salary_skills
from agents.base_agent import BaseAgent
from skills.loader import SkillLoader
from config.settings import settings
# === DỮ LIỆU GIẢ LẬP ===
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

# === HÀM LẤY THÔNG TIN USER ===
def get_user_info(user_id: str) -> dict:
    return EMPLOYEE_INFO.get(user_id, {"name": "Unknown", "role": "employee"})

# === KHỞI TẠO SKILL SYSTEM ===
skill_registry = SkillRegistry()
skill_factory = SkillFactory()

# Đăng ký built-in skills
for skill in all_salary_skills:
    skill_registry.register(skill, ["salary_management"])

# Tạo các agent với skill support
salary_agent_with_skills = BaseAgent(
    name="Salary Management Agent",
    agent_id="salary_management",
    skill_registry=skill_registry
)

# Bật các skills mặc định
salary_agent_with_skills.enable_skill("self_salary")
salary_agent_with_skills.enable_skill("bonus_calculator")
salary_agent_with_skills.enable_skill("salary_report")

# Tự động nạp custom skills từ ổ đĩa
SkillLoader.load_custom_skills(skill_registry)

# Bật tất cả custom skills đã nạp lên cho agent tương ứng
for skill in skill_registry.list_all():
    if skill.id not in ["self_salary", "bonus_calculator", "salary_report"]:
        agent_id = skill.metadata.get("agent_id", "salary_management")
        if agent_id == "salary_management":
            salary_agent_with_skills.enable_skill(skill.id)

# === STATE ===
class MultiAgentState(TypedDict):
    user_id: str
    user_role: Literal["employee", "accountant", "admin"]
    user_name: str
    query: str
    target_agent: Literal["hr_policies", "salary_management", "system_admin", "unknown"]
    access_granted: bool
    agent_response: str

# === NODE ĐỊNH TUYẾN & KIỂM SOÁT TRUY CẬP (Router & RBAC Node) ===
def router_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    user_role = state["user_role"]
    user_name = state["user_name"]
    
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        base_url=settings.LLM_BASE_URL,
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
    
    try:
        response = llm.invoke(messages)
        target_agent = response.content.strip().lower().replace("'", "").replace('"', '')
    except Exception as e:
        print(f"⚠️ Lỗi định tuyến: {e}. Dùng mặc định 'unknown'")
        target_agent = "unknown"
        
    if target_agent not in ["hr_policies", "salary_management", "system_admin", "unknown"]:
        target_agent = "unknown"
        
    state["target_agent"] = target_agent
    
    # Bản đồ quyền hạn
    role_permissions = {
        "employee": ["hr_policies", "salary_management"],
        "accountant": ["hr_policies", "salary_management"],
        "admin": ["hr_policies", "salary_management", "system_admin"]
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

# === NODE AGENT 1: QUY CHẾ & PHÚC LỢI (HR Agent) ===
def hr_policies_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    
    hr_documents = (
        "QUY CHẾ NỘI BỘ VÀ CHẾ ĐỘ PHÚC LỢI CÔNG TY:\n"
        "1. Thời gian làm việc: Từ 8:00 đến 17:30 hằng ngày, từ thứ Hai đến thứ Sáu. Nghỉ trưa từ 12:00 đến 13:30.\n"
        "2. Nghỉ phép năm: Nhân viên chính thức có 12 ngày phép năm hưởng nguyên lương. Cứ mỗi 5 năm thâm niên được thêm 1 ngày phép.\n"
        "3. Chế độ bảo hiểm: BHXH, BHYT, BHTN được đóng 100% dựa trên mức lương thực nhận hợp đồng.\n"
        "4. Lễ tết & Thưởng: Thưởng Quốc khánh (2/9), Giải phóng (30/4) là 1.000.000 VND/người. Thưởng tết Nguyên Đán lương tháng 13 dựa trên đánh giá KPI năm.\n"
        "5. Quy định trang phục: Trang phục lịch sự công sở vào thứ Hai đến thứ Năm. Thứ Sáu được phép mặc trang phục tự do."
    )
    
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        base_url=settings.LLM_BASE_URL,
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

# === NODE AGENT 2: QUẢN LÝ LƯƠNG (Salary Agent sử dụng skill system) ===
async def salary_management_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    user_role = state["user_role"]
    user_name = state["user_name"]
    
    context = {}
    if user_role == "employee":
        context["salary_data"] = SALARY_DB.get(user_name, {})
        context["access_level"] = "self"
    else:
        context["salary_data"] = SALARY_DB
        context["access_level"] = "all"
    
    context["user_name"] = user_name
    context["user_role"] = user_role
    
    response = await salary_agent_with_skills.process(query, user_role, context)
    state["agent_response"] = response
    return state

# === NODE AGENT 3: QUẢN TRỊ HỆ THỐNG (System Admin Agent) ===
def system_admin_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    
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
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        base_url=settings.LLM_BASE_URL,
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
    else:
        return "general_handler"

# === XÂY DỰNG ĐỒ THỊ ===
def build_multi_agent_system():
    workflow = StateGraph(MultiAgentState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("hr_policies", hr_policies_node)
    workflow.add_node("salary_management", salary_management_node)
    workflow.add_node("system_admin", system_admin_node)
    workflow.add_node("general_handler", general_handler_node)
    
    workflow.set_entry_point("router")
    
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
    
    workflow.add_edge("hr_policies", END)
    workflow.add_edge("salary_management", END)
    workflow.add_edge("system_admin", END)
    workflow.add_edge("general_handler", END)
    
    return workflow.compile()

# === HÀM CHẠY TƯƠNG TÁC ===
async def run_interactive():
    chatbot = build_multi_agent_system()
    
    print("\n" + "=" * 65)
    print("   🌐 HỆ THỐNG ĐA AGENT VỚI SKILL SYSTEM 🌐")
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
    print("Chức năng đặc biệt:")
    print("  - Gõ /skills để liệt kê kỹ năng khả dụng.")
    print("  - Gõ /create_skill [mô tả] để tự động tạo kỹ năng mới.")
    print("  - Gõ 'exit' hoặc 'quit' để kết thúc.")
    print("-" * 65)
    
    while True:
        try:
            query = input(f"\n👤 {name} ({role.upper()}) > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                print("\n👋 Đã thoát phiên làm việc. Tạm biệt!")
                break
                
            if query.lower() == "/skills":
                skills = salary_agent_with_skills.get_available_skills(role)
                print("\n📚 SKILLS KHẢ DỤNG:")
                if not skills:
                    print("  (Không có skill khả dụng cho vai trò này)")
                for s in skills:
                    print(f"  - {s.name}: {s.description}")
                continue
                
            if query.lower().startswith("/create_skill"):
                description = query.replace("/create_skill", "").strip()
                if not description:
                    print("❌ Vui lòng nhập mô tả skill. Ví dụ: /create_skill Tính thưởng theo thâm niên")
                    continue
                    
                print("⏳ Đang tạo skill từ mô tả của bạn...")
                new_skill = await skill_factory.create_from_description(
                    user_description=description,
                    agent_id="salary_management",
                    created_by=name
                )
                skill_registry.register(new_skill, ["salary_management"])
                salary_agent_with_skills.enable_skill(new_skill.id)
                
                # Lưu skill vào ổ đĩa để duy trì khi khởi động lại (persistence)
                try:
                    skill_file = os.path.join(settings.SKILLS_DIR, f"{new_skill.id}.json")
                    os.makedirs(os.path.dirname(skill_file), exist_ok=True)
                    with open(skill_file, "w", encoding="utf-8") as f:
                        f.write(new_skill.model_dump_json(indent=4))
                    print(f"💾 Đã lưu file cấu hình skill tại: {skill_file}")
                except Exception as e:
                    print(f"⚠️ Lỗi không thể lưu skill vào ổ đĩa: {e}")
                    
                print(f"✅ Đã tạo và kích hoạt skill: {new_skill.name}")
                continue
            
            # Xử lý query bình thường
            result = await chatbot.ainvoke({
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
            print(f"\n❌ Lỗi: {e}")

if __name__ == "__main__":
    asyncio.run(run_interactive())