from .workflow_state import MultiAgentState
from .instances import hr_agent_with_skills

# === NODE AGENT 1: QUY CHẾ & PHÚC LỢI (HR Agent) ===
async def hr_policies_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    user_role = state["user_role"]
    user_name = state["user_name"]
    
    hr_documents = (
        "QUY CHẾ NỘI BỘ VÀ CHẾ ĐỘ PHÚC LỢI CÔNG TY:\n"
        "1. Thời gian làm việc: Từ 8:00 đến 17:30 hằng ngày, từ thứ Hai đến thứ Sáu. Nghỉ trưa từ 12:00 đến 13:30.\n"
        "2. Nghỉ phép năm: Nhân viên chính thức có 12 ngày phép năm hưởng nguyên lương. Cứ mỗi 5 năm thâm niên được thêm 1 ngày phép.\n"
        "3. Chế độ bảo hiểm: BHXH, BHYT, BHTN được đóng 100% dựa trên mức lương thực nhận hợp đồng.\n"
        "4. Lễ tết & Thưởng: Thưởng Quốc khánh (2/9), Giải phóng (30/4) là 1.000.000 VND/người. Thưởng tết Nguyên Đán lương tháng 13 dựa trên đánh giá KPI năm.\n"
        "5. Quy định trang phục: Trang phục lịch sự công sở vào thứ Hai đến thứ Năm. Thứ Sáu được phép mặc trang phục tự do."
    )
    
    context = {
        "hr_documents": hr_documents,
        "user_name": user_name,
        "user_role": user_role
    }
    
    response = await hr_agent_with_skills.process(query, user_role, context)
    state["agent_response"] = response
    return state
