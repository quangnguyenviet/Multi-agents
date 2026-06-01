# base agent class
from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from config.settings import settings
from skills.registry import SkillRegistry
from skills.base import Skill

class BaseAgent:
    """Agent cơ bản có khả năng sử dụng skills và tools"""
    
    def __init__(self, name: str, agent_id: str, skill_registry: SkillRegistry, tools: List[Any] = None):
        self.name = name
        self.agent_id = agent_id
        self.skill_registry = skill_registry
        self.tools = tools if tools else []
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=0.2
        )
        self.enabled_skill_ids: List[str] = []
        
    def enable_skill(self, skill_id: str):
        """Bật một skill cho agent này"""
        if skill_id not in self.enabled_skill_ids:
            self.enabled_skill_ids.append(skill_id)
            print(f"✅ Enabled skill {skill_id} for agent {self.name}")
            
    def disable_skill(self, skill_id: str):
        """Tắt skill"""
        if skill_id in self.enabled_skill_ids:
            self.enabled_skill_ids.remove(skill_id)
            print(f"❌ Disabled skill {skill_id} for agent {self.name}")
    
    def get_available_skills(self, user_role: str) -> List[Skill]:
        """Lấy danh sách skills khả dụng (đã bật + có quyền)"""
        all_skills = self.skill_registry.get_skills_for_agent(self.agent_id, user_role)
        return [s for s in all_skills if s.id in self.enabled_skill_ids]
    
    def _select_best_skill(self, query: str, user_role: str) -> Optional[Skill]:
        """Chọn skill phù hợp nhất cho câu hỏi"""
        # Tìm skills theo từ khóa
        relevant = self.skill_registry.find_by_keywords(query, self.agent_id, user_role)
        
        if not relevant:
            return None
            
        # Chọn skill có điểm cao nhất
        best_skill, best_score = relevant[0]
        print(f"🎯 [SKILL] Agent {self.name} sử dụng skill: {best_skill.name} (score: {best_score})")
        return best_skill
    
    async def process(self, query: str, user_role: str, context: Dict = None) -> str:
        """Xử lý câu hỏi - chọn và thực thi skill phù hợp"""
        
        # 1. Tìm skill phù hợp
        selected_skill = self._select_best_skill(query, user_role)
        
        if not selected_skill:
            # 2. Fallback: dùng prompt mặc định
            return await self._default_response(query, context, user_role)
        
        # 3. Thực thi skill được chọn
        return await self._execute_skill(selected_skill, query, context, user_role)
    
    def _get_allowed_tools(self, user_role: str) -> List[Any]:
        """Lọc danh sách tools dựa trên vai trò (RBAC)"""
        allowed = []
        for t in self.tools:
            if t.name == "get_company_employee_list":
                if user_role in ["admin", "accountant"]:
                    allowed.append(t)
                else:
                    print(f"🔒 [SECURITY] Chặn cuộc gọi tool get_company_employee_list cho vai trò: {user_role}")
            else:
                allowed.append(t)
        return allowed

    async def _execute_skill(self, skill: Skill, query: str, context: Dict, user_role: str) -> str:
        """Thực thi một skill cụ thể kèm gọi Tool tự động nếu có"""
        skill_prompt = f"""
{skill.system_prompt}

Dữ liệu context (nếu có):
{context if context else 'Không có context bổ sung'}

Câu hỏi của người dùng: {query}
"""
        messages = [
            SystemMessage(content=(
                "Bạn là trợ lý AI thực thi skill được chỉ định. Bạn có khả năng sử dụng các tools được cung cấp để tra cứu thông tin chính xác khi cần.\n"
                "QUY TẮC QUAN TRỌNG KHI SỬ DỤNG TOOL:\n"
                "- Nếu cần dữ liệu để trả lời câu hỏi, bạn PHẢI kích hoạt cuộc gọi tool tương ứng qua hệ thống. Tuyệt đối KHÔNG tự bịa đặt hoặc giả lập thông tin khi chưa có kết quả từ tool.\n"
                "- Khi gọi tool, hãy sử dụng tính năng gọi tool tích hợp của hệ thống. Tuyệt đối KHÔNG tự viết mã JSON (như '{}') hay bất kỳ cú pháp giả lập nào vào phần nội dung tin nhắn phản hồi của bạn.\n"
                "- Sau khi đã nhận được dữ liệu phản hồi từ tool ở lượt tiếp theo, bạn mới tiến hành định dạng, sắp xếp thông tin (ví dụ: vẽ bảng Markdown) để trả lời người dùng một cách đầy đủ và chính xác."
            )),
            HumanMessage(content=skill_prompt)
        ]
        
        allowed_tools = self._get_allowed_tools(user_role)
        
        # Nếu Agent có trang bị tools, thực hiện bind_tools vào LLM
        if allowed_tools:
            llm_with_tools = self.llm.bind_tools(allowed_tools)
        else:
            llm_with_tools = self.llm
            
        response = llm_with_tools.invoke(messages)
        
        iterations = 0
        max_iterations = 5  # Tránh lặp vô hạn
        
        while response.tool_calls and iterations < max_iterations:
            messages.append(response)
            iterations += 1
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Tìm tool phù hợp trong danh sách của Agent
                matched_tool = next((t for t in allowed_tools if t.name == tool_name), None)
                if matched_tool:
                    try:
                        tool_output = matched_tool.invoke(tool_args)
                    except Exception as e:
                        tool_output = f"Lỗi khi thực thi tool: {e}"
                else:
                    tool_output = f"Lỗi: Không tìm thấy tool {tool_name} hoặc bạn không có quyền truy cập"
                
                messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"]))
                print(f"🛠️ [TOOL] Agent {self.name} sử dụng tool: {tool_name} | Tham số: {tool_args} | Kết quả: {str(tool_output).strip()}")
                
            response = llm_with_tools.invoke(messages)
            
        return response.content
    
    async def _default_response(self, query: str, context: Dict, user_role: str) -> str:
        """Phản hồi mặc định khi không có skill phù hợp"""
        messages = [
            SystemMessage(content=(
                f"Bạn là {self.name} agent. Hãy trả lời câu hỏi của người dùng một cách hữu ích.\n"
                "Nếu cần dữ liệu chính xác để trả lời, bạn PHẢI kích hoạt cuộc gọi tool tương ứng qua hệ thống. Tuyệt đối KHÔNG tự bịa đặt thông tin."
            )),
            HumanMessage(content=query)
        ]
        
        allowed_tools = self._get_allowed_tools(user_role)
        
        # Nếu Agent có trang bị tools, thực hiện bind_tools vào LLM
        if allowed_tools:
            llm_with_tools = self.llm.bind_tools(allowed_tools)
        else:
            llm_with_tools = self.llm
            
        response = llm_with_tools.invoke(messages)
        
        iterations = 0
        max_iterations = 5
        
        while response.tool_calls and iterations < max_iterations:
            messages.append(response)
            iterations += 1
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                matched_tool = next((t for t in allowed_tools if t.name == tool_name), None)
                if matched_tool:
                    try:
                        tool_output = matched_tool.invoke(tool_args)
                    except Exception as e:
                        tool_output = f"Lỗi khi thực thi tool: {e}"
                else:
                    tool_output = f"Lỗi: Không tìm thấy tool {tool_name} hoặc bạn không có quyền truy cập"
                
                messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"]))
                print(f"🛠️ [TOOL] Agent {self.name} sử dụng tool: {tool_name} | Tham số: {tool_args} | Kết quả: {str(tool_output).strip()}")
                
            response = llm_with_tools.invoke(messages)
            
        return response.content