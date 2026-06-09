from langchain_core.tools import tool
import datetime
import math


@tool
def calculate(expression: str) -> str:
    """Tính toán biểu thức toán học. Hỗ trợ: +, -, *, /, **, %, sqrt(), log(), sin(), cos().
    Ví dụ: '15% of 8000000', '2**10', 'sqrt(144)', '1234 * 5678'.
    """
    try:
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
        f"Thứ: {['Thứ Hai','Thứ Ba','Thứ Tư','Thứ Năm','Thứ Sáy','Thứ Bảy','Chủ Nhật'][now.weekday()]}\n"
        f"Tuần trong năm: tuần {now.isocalendar()[1]}"
    )
