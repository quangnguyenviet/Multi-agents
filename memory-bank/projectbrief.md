# Project Brief: Multi-Agent Skill Studio

Hệ thống Chatbot Đa Agent (Multi-Agent System) có khả năng tự động định tuyến yêu cầu, quản lý quyền hạn người dùng (RBAC) và cho phép quản trị viên thiết kế, lưu trữ các kỹ năng (Skills) của Agent động qua giao diện Web mà không cần thay đổi mã nguồn backend.

## Mục tiêu chính
- **Đa Agent phân quyền**: Hỗ trợ 3 Agents chính: HR Policies, Salary Management, System Admin.
- **Dynamic Skill Studio**: Quản lý (Thêm, Xóa, Lưu lâu dài) các Kỹ năng dưới dạng tệp JSON tại thư mục `storage/custom_skills/`.
- **Tool Calling linh hoạt**: Tích hợp các công cụ tra cứu thực tế (LangChain Tools) giúp Agent giải quyết câu hỏi chéo ngữ cảnh tự động.
- **Giao diện Trải nghiệm cao (UI/UX)**: Bảng điều khiển admin mượt mà, phân quyền hiển thị theo thời gian thực.
