# main.py - Điểm khởi chạy CLI tương tác với chatbot
import os
import asyncio
from data import database as db
from config.settings import settings

# Import Agent instances and compiled chatbot graph
from agents import (
    chatbot,
    skill_registry,
    skill_factory,
    hr_agent_with_skills,
    salary_agent_with_skills,
    system_admin_agent_with_skills
)

# === HÀM CHẠY TƯƠNG TÁC ===
async def run_interactive():
    print("\n" + "=" * 65)
    print("   🌐 HỆ THỐNG ĐA AGENT VỚI SKILL SYSTEM 🌐")
    print("=" * 65)
    
    print("\nDanh sách tài khoản giả lập trong hệ thống:")
    employees = db.get_all_employees()
    for emp in employees:
        print(f"  - ID: {emp['user_id']:<8} | Tên: {emp['name']:<15} | Vai trò: {emp['role'].upper()}")
    
    # Đăng nhập
    user_id = ""
    while not user_id:
        uid_input = input("\n👉 Nhập User ID của bạn để đăng nhập (ví dụ: emp_001, acc_001, adm_001): ").strip()
        if db.check_user_exists(uid_input):
            user_id = uid_input
        else:
            print("❌ ID tài khoản không tồn tại. Vui lòng thử lại!")

    user_info = db.get_user_info_safe(user_id)
    name = user_info["name"]
    role = user_info["role"]

    print(f"\n✅ ĐĂNG NHẬP THÀNH CÔNG!")
    print(f"👤 Người dùng: {name}")
    print(f"🔑 Vai trò: {role.upper()}")
    print("-" * 65)
    print("Bắt đầu đặt câu hỏi cho hệ thống đa Agent.")
    print("Chức năng đặc biệt:")
    print("  - Gõ /agents để xem danh sách Agent và phân quyền truy cập.")
    print("  - Gõ /skills [agent_id] để liệt kê các kỹ năng của Agent cụ thể.")
    print("  - Gõ /create_skill [agent_id] [mô tả] để tạo kỹ năng mới (Chỉ ADMIN).")
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
                
            if query.lower() == "/agents":
                agents_info = {
                    "hr_policies": {
                        "name": "HR Policies Agent",
                        "description": "Giải đáp quy định, quy chế công ty, chế độ phép năm, bảo hiểm.",
                        "allowed_roles": ["employee", "accountant", "admin"]
                    },
                    "salary_management": {
                        "name": "Salary Management Agent",
                        "description": "Quản lý và tra cứu thông tin bảng lương, tính thưởng và báo cáo lương.",
                        "allowed_roles": ["employee", "accountant", "admin"]
                    },
                    "system_admin": {
                        "name": "System Admin Agent",
                        "description": "Theo dõi và giám sát hiệu năng máy chủ, CPU, RAM và log hệ thống.",
                        "allowed_roles": ["admin"]
                    }
                }
                print("\n🤖 DANH SÁCH AGENTS TRONG HỆ THỐNG:")
                for aid, ainfo in agents_info.items():
                    is_accessible = role in ainfo["allowed_roles"]
                    status = "✅ Được phép truy cập" if is_accessible else "❌ Bị khóa (Không có quyền)"
                    print(f"  🔹 {ainfo['name']} (`{aid}`):")
                    print(f"      Mô tả: {ainfo['description']}")
                    print(f"      Quyền truy cập của bạn: {status}")
                continue
                
            if query.lower().startswith("/skills"):
                args = query.replace("/skills", "").strip()
                if not args:
                    print("\n💡 Hướng dẫn sử dụng: Gõ `/skills [agent_id]` để liệt kê kỹ năng của Agent đó.")
                    print("Các Agent khả dụng của bạn:")
                    available_agents = []
                    if role in ["employee", "accountant", "admin"]:
                        available_agents.append("  - `hr_policies` (HR Agent)")
                        available_agents.append("  - `salary_management` (Salary Agent)")
                    if role == "admin":
                        available_agents.append("  - `system_admin` (System Admin Agent)")
                    for aa in available_agents:
                        print(aa)
                    continue
                
                target_agent_id = args.lower()
                
                # Phân quyền
                role_permissions = {
                    "employee": ["hr_policies", "salary_management"],
                    "accountant": ["hr_policies", "salary_management"],
                    "admin": ["hr_policies", "salary_management", "system_admin"]
                }
                
                allowed = role_permissions.get(role, [])
                if target_agent_id not in ["hr_policies", "salary_management", "system_admin"]:
                    print(f"❌ Agent ID `{target_agent_id}` không tồn tại.")
                    continue
                    
                if target_agent_id not in allowed:
                    print(f"❌ Bạn không có quyền xem kỹ năng của Agent `{target_agent_id}`.")
                    continue
                
                # Lấy danh sách skill của agent tương ứng
                if target_agent_id == "hr_policies":
                    skills = hr_agent_with_skills.get_available_skills(role)
                    agent_name = "HR Policies Agent"
                elif target_agent_id == "salary_management":
                    skills = salary_agent_with_skills.get_available_skills(role)
                    agent_name = "Salary Management Agent"
                else:
                    skills = system_admin_agent_with_skills.get_available_skills(role)
                    agent_name = "System Admin Agent"
                
                print(f"\n📚 SKILLS KHẢ DỤNG CỦA [{agent_name.upper()}]:")
                if not skills:
                    print("  (Không có skill khả dụng hoặc bạn không có quyền)")
                for s in skills:
                    print(f"  - {s.name}: {s.description}")
                continue
                
            if query.lower().startswith("/create_skill"):
                # 1. Kiểm tra quyền Admin
                if role != "admin":
                    print("❌ Quyền truy cập bị từ chối! Chỉ tài khoản vai trò quản trị viên (ADMIN) mới có quyền tạo kỹ năng mới.")
                    continue
                
                content = query.replace("/create_skill", "").strip()
                if not content:
                    print("\n❌ Cú pháp sai! Vui lòng sử dụng cú pháp: `/create_skill [agent_id] [mô tả]`")
                    print("Ví dụ: `/create_skill salary_management Tính thưởng Tết theo thâm niên`")
                    print("Các Agent ID khả dụng: `hr_policies`, `salary_management`, `system_admin`")
                    continue
                
                # 2. Tách từ đầu tiên làm agent_id, phần còn lại là mô tả
                parts = content.split(" ", 1)
                target_agent_id = parts[0].strip().lower()
                
                valid_agents = ["hr_policies", "salary_management", "system_admin"]
                if target_agent_id not in valid_agents:
                    print(f"\n❌ Lỗi: Agent ID `{target_agent_id}` không hợp lệ!")
                    print("Vui lòng nhập đúng Agent ID làm từ đầu tiên. Ví dụ: `/create_skill salary_management Tính thưởng`")
                    print("Các Agent ID hợp lệ: `hr_policies`, `salary_management`, `system_admin`")
                    continue
                    
                if len(parts) < 2 or not parts[1].strip():
                    print("❌ Lỗi: Vui lòng cung cấp mô tả chi tiết của kỹ năng. Ví dụ: `/create_skill salary_management Tính thưởng Tết`")
                    continue
                
                description = parts[1].strip()
                
                print(f"⏳ Đang sử dụng AI để thiết kế Skill và gán cho Agent `{target_agent_id}`...")
                new_skill = await skill_factory.create_from_description(
                    user_description=description,
                    agent_id=target_agent_id,
                    created_by=name
                )
                
                # 3. Đăng ký vào Registry cho agent tương ứng
                skill_registry.register(new_skill, [target_agent_id])
                
                # 4. Kích hoạt trực tiếp lên agent tương ứng
                if target_agent_id == "hr_policies":
                    hr_agent_with_skills.enable_skill(new_skill.id)
                elif target_agent_id == "salary_management":
                    salary_agent_with_skills.enable_skill(new_skill.id)
                elif target_agent_id == "system_admin":
                    system_admin_agent_with_skills.enable_skill(new_skill.id)
                
                # 5. Lưu skill vào ổ đĩa để duy trì (persistence)
                try:
                    skill_file = os.path.join(settings.SKILLS_DIR, f"{new_skill.id}.json")
                    os.makedirs(os.path.dirname(skill_file), exist_ok=True)
                    with open(skill_file, "w", encoding="utf-8") as f:
                        f.write(new_skill.model_dump_json(indent=4))
                    print(f"💾 Đã lưu file cấu hình skill tại: {skill_file}")
                except Exception as e:
                    print(f"⚠️ Lỗi không thể lưu skill vào ổ đĩa: {e}")
                    
                print(f"✅ Đã tạo, lưu trữ và kích hoạt skill: {new_skill.name} cho Agent: {target_agent_id}")
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