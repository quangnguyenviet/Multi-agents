# Active Context

## Trọng tâm phát triển hiện tại
Đã hoàn thành đơn giản hóa kiến trúc: **Gộp toàn bộ agent nodes thành 1 LLM node duy nhất** + **Loại bỏ RBAC tạm thời** + **Dọn dẹp frontend không còn chọn/quản lý agents**.

1. **🔀 Đơn giản hóa LangGraph Workflow** ✅:
   - Topology mới: `START → llm → END` (từ 7 nodes xuống 2 nodes).
   - Xóa 6 file node cũ: `hr_agent.py`, `salary_agent.py`, `admin_agent.py`, `user_agent.py`, `router.py`, `general_handler.py`.
   - Tạo `backend/agents/llm_node.py`: gọi thẳng ChatOpenAI (9Router), không skill, không RBAC.
   - `MultiAgentState` rút gọn còn 4 field: `user_id`, `user_name`, `query`, `agent_response`.

2. **🖥️ Đơn giản hóa Frontend** ✅:
   - Bỏ dropdown chọn agent trong chat header.
   - Bỏ route và sidebar link "Quản lý Agents".
   - Chat gửi `POST /api/chat` chỉ với `{user_id, query}`, nhận về `{response}`.
   - `ChatWorkspace.jsx`: header tĩnh "AI Assistant".
   - `ChatInputBar.jsx`: 3 generic chips thay vì chips theo từng agent.
   - Giữ lại: Quản lý Kỹ năng, Quản lý Tools, CV Processor.

## Hoàn thành gần đây
- **🔀 Single LLM Node**: `backend/agents/llm_node.py` — ChatOpenAI (9Router `evotek_flash`, temp 0.7), system prompt chung "trợ lý AI nội bộ thân thiện".
- **📦 Dọn dẹp backend**: Xóa 6 agent node files không còn dùng. Giữ `base_agent.py` + `instances.py` vì `routes.py` vẫn dùng skill enable/disable.
- **🎨 Dọn dẹp frontend**: Bỏ `AgentManager.jsx`, `AgentModal.jsx` khỏi render tree. Bỏ `activeAgent`/`agents` state khỏi App.jsx.

## Cấu trúc backend/agents/ hiện tại
```
backend/agents/
├── workflow.py         ← START → llm → END
├── workflow_state.py   ← 4 fields: user_id, user_name, query, agent_response
├── llm_node.py         ← single LLM node (ChatOpenAI)
├── base_agent.py       ← còn dùng bởi instances.py
├── instances.py        ← skill_registry + 4 agent instances (cho skill management)
└── __init__.py
```

## Lưu ý kỹ thuật quan trọng
- `instances.py` và `base_agent.py` vẫn cần giữ — `routes.py` dùng chúng để enable/disable skill trên từng agent instance khi publish/delete skill.
- `cv_agent.py` phải đặt ở `backend/` root, **không** trong `backend/agents/` — tránh UnicodeEncodeError Windows cp1252.
- Prompt template CV dùng `.replace()` thay vì `.format()` để tránh `KeyError` với `{}` trong JSON schema.

## Nhiệm vụ tiếp theo
- **Xác thực JWT**: Nâng cấp phân quyền từ `user_id` query param hiện tại sang Token JWT bảo mật (`Authorization: Bearer <token>`).
- **Cải thiện UI/UX**: Loading skeletons, error boundaries.
- **Testing & Error Handling**: Edge cases (network failure, LLM timeout).
