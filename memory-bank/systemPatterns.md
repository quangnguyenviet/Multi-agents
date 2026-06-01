# System Patterns

## Kiến trúc Hệ thống

### 1. Đồ thị LangGraph Workflow & Định tuyến Động
- **`MultiAgentState`**: Lưu trữ trạng thái phiên chat (`user_id`, `user_role`, `query`, `target_agent`, `access_granted`, `agent_response`).
- **`router_node`**: Xác minh RBAC và định hướng luồng dựa trên lựa chọn active tab hoặc tự động phân loại của LLM.
- **`Auto-Router`**: Đóng vai trò là nút trung gian phân tích ý định (Intent Classifier) để chuyển hướng cuộc gọi đến Agent phù hợp nhất, đồng thời cho phép gán cứng Agent thủ công để ghi đè.
- **Agent Nodes**: `hr_policies_node`, `salary_management_node`, `system_admin_node` thực hiện đóng gói context nội bộ và gọi `BaseAgent.process()`.

### 2. Kiến trúc ReactJS Client (Modular State)
- **`App.jsx` Core Controller**:
  - Đóng vai trò là bộ não quản lý trạng thái tập trung (Single Source of Truth) lưu trữ danh sách: `agents`, `skills`, `tools`, `chatMessages`, `currentUser`, và `activeTab`.
  - Các thao tác cập nhật (như lưu System Prompt, bật/tắt kích hoạt Tool, duyệt kỹ năng nháp HITL) sẽ thay đổi trực tiếp State và hiển thị đồng bộ lên UI ngay tức khắc.
- **Thiết kế Responsive Full-bleed**:
  - Sidebar (Menu trái) chịu trách nhiệm phân quyền RBAC và chuyển tab.
  - Workspace Panel (Phải) co giãn tự do chiếm 100% diện tích màn hình còn lại (sau khi đã gỡ bỏ cột live logs bên phải theo yêu cầu), đảm bảo tính thẩm mỹ cao nhất.

### 3. Tích hợp Tool Calling & Web Proxy
- **9Router LLM Proxy**: Backend kết nối LLM qua 9Router (`http://172.31.2.23:20128/v1`) thay vì gọi thẳng Groq. 9Router hoạt động như một API gateway thông minh: nén token, dịch format API, và fallback đa tầng (Subscription → Cheap → Free).
- **Vite Proxy Engine**: Chuyển hướng các request `/api` từ giao diện phát triển (cổng 3000) về FastAPI backend (cổng 8000), loại bỏ triệt để lỗi CORS khi chạy dev.
- **FastAPI Static Mounts**:
  - Tự động mount tệp React build từ `/frontend/dist/assets` vào đường dẫn `/assets` để phục vụ SPA tĩnh hợp nhất trên cổng 8000.
