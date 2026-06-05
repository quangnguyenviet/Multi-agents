from langchain_core.tools import tool
import requests
import datetime
import math
import json
import os
from data import database as db

_COMPANY_INFO_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "company_info.json")

@tool
def get_company_info() -> str:
    """Lấy thông tin tổng quan về công ty: tên, địa chỉ, phòng ban, phúc lợi, giờ làm việc, sứ mệnh.
    Dùng khi người dùng hỏi về công ty, tổ chức, chính sách, liên hệ."""
    with open(os.path.normpath(_COMPANY_INFO_PATH), encoding="utf-8") as f:
        info = json.load(f)

    depts = "\n".join(
        f"  • {d['name']} (trưởng phòng: {d['head']}, {d['size']} người)"
        for d in info["departments"]
    )
    benefits = "\n".join(f"  • {b}" for b in info["benefits"])

    return (
        f"THÔNG TIN CÔNG TY (từ hệ thống nội bộ):\n"
        f"Tên: {info['name']} | Thành lập: {info['founded']}\n"
        f"Ngành: {info['industry']}\n"
        f"Trụ sở: {info['headquarters']}\n"
        f"Liên hệ: {info['phone']} | {info['email']} | {info['website']}\n"
        f"Nhân sự: {info['employee_count']} người\n"
        f"Giờ làm việc: {info['working_hours']}\n"
        f"Sứ mệnh: {info['mission']}\n"
        f"Phòng ban:\n{depts}\n"
        f"Phúc lợi:\n{benefits}"
    )

@tool
def calculate(expression: str) -> str:
    """Tính toán biểu thức toán học. Hỗ trợ: +, -, *, /, **, %, sqrt(), log(), sin(), cos().
    Ví dụ: '15% of 8000000', '2**10', 'sqrt(144)', '1234 * 5678'.
    """
    try:
        # Chuẩn hoá: "X% of Y" → "X/100*Y"
        import re
        expr = expression.strip()
        expr = re.sub(r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)', r'(\1/100*\2)', expr, flags=re.IGNORECASE)
        expr = expr.replace('%', '/100')

        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
        result = eval(expr, {"__builtins__": {}}, allowed)  # noqa: S307

        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"Kết quả: {expression} = {result:,}"
    except Exception as e:
        return f"Không thể tính '{expression}': {e}"

@tool
def get_current_datetime() -> str:
    """Lấy ngày giờ hiện tại của hệ thống. Dùng khi người dùng hỏi về thời gian, ngày tháng, giờ hiện tại."""
    now = datetime.datetime.now()
    return (
        f"Ngày giờ hiện tại: {now.strftime('%A, %d/%m/%Y %H:%M:%S')}\n"
        f"Thứ: {['Thứ Hai','Thứ Ba','Thứ Tư','Thứ Năm','Thứ Sáu','Thứ Bảy','Chủ Nhật'][now.weekday()]}\n"
        f"Tuần trong năm: tuần {now.isocalendar()[1]}"
    )

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
