# System Patterns

## Kiến trúc Hệ thống

### 1. LangGraph Workflow (Đã đơn giản hóa)
- **Topology**: `START → llm → END` (2 nodes)
- **`MultiAgentState`**: 4 field — `user_id`, `user_name`, `query`, `agent_response`
- **`llm_node`** (`backend/agents/llm_node.py`): Gọi thẳng ChatOpenAI (9Router), system prompt chung, temperature 0.7
- **Không còn**: router_node, RBAC, agent-specific context injection, skill selection trong workflow

### 2. Skill System (Tách biệt khỏi Workflow)
- `instances.py` vẫn duy trì 4 `BaseAgent` instances và `SkillRegistry` — dùng riêng cho skill enable/disable qua `/api/skills/publish`, `/api/delete_skill`
- Skills lưu trên đĩa dưới dạng JSON tại `storage/custom_skills/`
- Skill management (CRUD) vẫn hoạt động đầy đủ qua Admin UI

### 3. Kiến trúc ReactJS Client
- **`App.jsx` Core Controller**:
  - State chính: `currentUser`, `skills`, `tools`, `chatMessages`, `isTyping`
  - Không còn: `activeAgent`, `agents` state
  - Chat: gọi `POST /api/chat` với `{user_id, query}`, nhận `{response}`
- **Chat UI**: Header tĩnh "AI Assistant", 3 generic shortcut chips
- **Sidebar Admin** (role=admin): Quản lý Kỹ năng, Quản lý Tools (bỏ Quản lý Agents)
- **Thiết kế Full-bleed**: Sidebar trái + Content Panel 100% chiều rộng còn lại

### 4. Tích hợp LLM & Proxy
- **9Router LLM Proxy**: `http://172.31.2.23:20128/v1`, model `evotek_flash`
- **Vite Proxy**: Dev port 3000 → Backend port 8000 (loại bỏ CORS)
- **FastAPI Static**: Serve React build từ `/frontend/dist/`

### 5. CV Processor Pipeline
- `POST /api/cv/extract`: pdfplumber → LLM (9Router) → JSON có cấu trúc
- `POST /api/cv/render`: JSON data → Jinja2 template → HTML A4 2 cột
- Accessible mọi role đã đăng nhập

## File Structure Backend (agents/)
```
backend/agents/
├── workflow.py         ← build_multi_agent_system(), chatbot
├── workflow_state.py   ← MultiAgentState TypedDict
├── llm_node.py         ← def llm_node(state) → dict
├── base_agent.py       ← BaseAgent class (skill execution)
├── instances.py        ← skill_registry, 4 BaseAgent instances
└── __init__.py         ← exports chatbot, skill_registry, agent instances
```
