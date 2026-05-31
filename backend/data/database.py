import sqlite3
import os
from typing import Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "company.db")

def init_db():
    """Khởi tạo database, tạo bảng employees và chèn dữ liệu mẫu nếu bảng trống."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tạo bảng employees
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            user_id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            salary INTEGER NOT NULL
        )
    """)
    
    # Kiểm tra xem có dữ liệu chưa, nếu chưa có thì chèn dữ liệu mẫu (seeding)
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        initial_data = [
            ("emp_001", "Nguyen Van A", "employee", 15000000),
            ("emp_002", "Tran Thi B", "employee", 18000000),
            ("acc_001", "Le Van C", "accountant", 22000000),
            ("adm_001", "Nguyen Admin", "admin", 30000000)
        ]
        cursor.executemany(
            "INSERT INTO employees (user_id, name, role, salary) VALUES (?, ?, ?, ?)",
            initial_data
        )
        conn.commit()
        print("💾 [DATABASE] Khởi tạo thành công database và chèn dữ liệu mẫu.")
    conn.close()

def get_user_info(user_id: str) -> Optional[dict]:
    """Lấy thông tin cơ bản của user (tên, vai trò) bằng user_id."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, role FROM employees WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"name": row["name"], "role": row["role"]}
    return None

def get_all_employees() -> List[dict]:
    """Lấy danh sách thông tin cơ bản của tất cả nhân viên (dùng cho Tool)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, name, role FROM employees")
    rows = cursor.fetchall()
    conn.close()
    
    return [{"user_id": r["user_id"], "name": r["name"], "role": r["role"]} for r in rows]

def get_salary_data(name: str) -> Optional[dict]:
    """Lấy thông tin lương và vai trò của một nhân viên bằng tên (Họ và tên)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT salary, role FROM salaries WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"salary": row["salary"], "role": row["role"]}
    return None

def get_all_salaries() -> Dict[str, dict]:
    """Lấy toàn bộ thông tin bảng lương của tất cả nhân viên (dùng cho Accountant/Admin)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, salary, role FROM salaries")
    rows = cursor.fetchall()
    conn.close()
    
    result = {}
    for r in rows:
        result[r["name"]] = {"salary": r["salary"], "role": r["role"]}
    return result

def check_user_exists(user_id: str) -> bool:
    """Kiểm tra sự tồn tại của User ID trong cơ sở dữ liệu."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM employees WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_user_info_safe(user_id: str) -> dict:
    """Lấy thông tin user an toàn, trả về giá trị mặc định nếu không tồn tại."""
    info = get_user_info(user_id)
    if info:
        return info
    return {"name": "Unknown", "role": "employee"}

# Tự động khởi chạy init_db khi file này được import để đảm bảo DB luôn sẵn sàng
init_db()
