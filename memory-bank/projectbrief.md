# Project Brief: Multi-Agent Skill Studio

Hệ thống Chatbot doanh nghiệp với single LLM node (LangGraph ReAct), dynamic skill system lưu trên MinIO, và tool calling thực tế.

## Mục tiêu chính
- **Single LLM Node + Tool Calling**: 1 node LangGraph bind 8 tools, tự quyết định gọi tool nào.
- **Dynamic Skill (MinIO)**: Skill = file `.md` trên MinIO. Thêm skill không cần sửa code, không cần restart.
- **Tool Registry (code-first)**: Tool = `@tool` Python function. Derive từ code, không configurable qua UI.
- **User Management**: Đăng nhập username/password, RBAC (admin/user), Postgres.
