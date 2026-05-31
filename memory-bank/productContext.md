# Product Context

## Tại sao dự án này tồn tại?
Trong các hệ thống Chatbot doanh nghiệp thông thường, việc thay đổi hoặc thêm bớt các tính năng, hành vi của AI đòi hỏi lập trình viên phải sửa đổi trực tiếp mã nguồn Python tĩnh (hardcoded), dẫn đến tốn thời gian và rủi ro gián đoạn dịch vụ. 

Dự án này giải quyết bài toán đó bằng cách **động hóa 100% Kỹ năng của AI**:
- Cho phép Admin doanh nghiệp tự bổ sung nghiệp vụ cho chatbot thông qua ngôn ngữ tự nhiên ngay trên giao diện (Studio).
- Tách biệt hoàn toàn phần lõi xử lý (`main.py`) khỏi các định nghĩa kỹ năng (`storage/custom_skills/*.json`).

## Trải nghiệm mong muốn
- **Admin**: Tạo hoặc xóa kỹ năng nhanh chóng, định cấu hình prompt và quyền hạn trực quan.
- **Nhân viên**: Trò chuyện mượt mà, bảo mật tuyệt đối thông tin (không thể xem trộm lương của đồng nghiệp hoặc tài nguyên máy chủ nếu không được cấp quyền).
