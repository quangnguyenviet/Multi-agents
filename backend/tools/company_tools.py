from langchain_core.tools import tool
import requests
from data import database as db

@tool
def get_company_employee_list(*args, **kwargs) -> str:
    """Lấy danh sách họ và tên cùng mã User ID của toàn bộ nhân viên trong công ty."""
    report = "DANH SÁCH NHÂN VIÊN TOÀN CÔNG TY (TRUY XUẤT TỪ TOOL):\n"
    employees = db.get_all_employees()
    for emp in employees:
        report += f"- {emp['name']} (ID: {emp['user_id']}) | Vai trò: {emp['role'].upper()}\n"
    return report

@tool
def get_demo_users_list(*args, **kwargs) -> str:
    """Gọi API ngoài từ demo service để lấy danh sách toàn bộ người dùng dùng thử (Demo Users)."""
    try:
        response = requests.get("http://127.0.0.1:8080/api/test/users", timeout=3)
        if response.status_code == 200:
            users = response.json()
            report = "DANH SÁCH NGƯỜI DÙNG DEMO (TRUY XUẤT THÀNH CÔNG TỪ API CỔNG 8080):\n"
            for u in users:
                report += f"- {u['name']} (ID: {u['user_id']}) | Vai trò: {u['role'].upper()} | Email: {u['email']}\n"
            return report
        else:
            return f"❌ LỖI: API ngoài phản hồi mã lỗi {response.status_code}."
    except Exception as e:
        return "❌ LỖI KẾT NỐI: Không thể kết nối tới Demo Service tại cổng 8080. Vui lòng đảm bảo dịch vụ đã được khởi chạy bằng lệnh `python demo_service.py`."
