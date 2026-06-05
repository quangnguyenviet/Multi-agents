import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from data import database as db
from config.settings import settings
from skills.base import Skill, SkillType, Parameter, Permission

# Import storage modules
from storage import agent_store, tool_store

# Import Pydantic schemas
from .models import ChatRequest, CreateSkillRequest, PublishSkillRequest
from .models import AgentPromptRequest, CreateAgentRequest, CreateToolRequest, UpdateToolRequest

# Import Agent instances and chatbot graph
from agents import (
    chatbot,
    skill_registry,
    skill_factory,
    hr_agent_with_skills,
    salary_agent_with_skills,
    system_admin_agent_with_skills,
    user_management_agent_with_skills
)

router = APIRouter()

# API get user info and agent RBAC status
@router.get("/agents")
async def get_agents(user_id: str = Query(...)):
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    role = user_info["role"]

    agents_list = agent_store.get_agents_for_user(role)

    return {
        "user_id": user_id,
        "name": user_info["name"],
        "role": role,
        "agents": agents_list
    }

# API get skills for agent
@router.get("/skills")
async def get_skills(agent_id: str = Query(...), user_id: str = Query(...)):
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    role = user_info["role"]
    
    # Check permission
    role_permissions = {
        "employee": ["hr_policies", "salary_management"],
        "accountant": ["hr_policies", "salary_management", "user_management"],
        "admin": ["hr_policies", "salary_management", "system_admin", "user_management"]
    }
    
    allowed = role_permissions.get(role, [])
    if agent_id not in allowed:
        raise HTTPException(status_code=403, detail="Không có quyền xem kỹ năng của Agent này")
        
    skills = skill_registry.get_skills_for_agent(agent_id, role)
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "required_roles": s.permission.required_roles
        } for s in skills
    ]

# API chat with Multi-Agent system
@router.post("/chat")
async def chat(req: ChatRequest):
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    role = user_info["role"]
    name = user_info["name"]
    
    try:
        # Run compiled LangGraph
        result = await chatbot.ainvoke({
            "user_id": req.user_id,
            "user_role": role,
            "user_name": name,
            "query": req.query,
            "target_agent": req.active_agent,
            "access_granted": False,
            "agent_response": ""
        })
        
        target_agent = result.get("target_agent", "unknown")
        access_granted = result.get("access_granted", False)
        
        return {
            "response": result.get("agent_response", ""),
            "target_agent": target_agent,
            "access_granted": access_granted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chatbot: {e}")

# API draft new skill dynamically (Pha 1: AI sinh bản nháp)
@router.post("/skills/draft")
async def draft_skill(req: CreateSkillRequest):
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    role = user_info["role"]
    name = user_info["name"]
    
    if role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền thiết kế nháp skill mới")
        
    valid_agents = ["hr_policies", "salary_management", "system_admin", "user_management"]
    if req.agent_id not in valid_agents:
        raise HTTPException(status_code=400, detail=f"Agent ID `{req.agent_id}` không hợp lệ")
        
    try:
        # Build using SkillFactory (chỉ sinh nháp, không lưu hay đăng ký)
        draft = await skill_factory.create_from_description(
            user_description=req.description,
            agent_id=req.agent_id,
            created_by=name
        )
        return {
            "success": True,
            "skill": draft.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi thiết kế nháp skill: {e}")

# API publish reviewed skill dynamically (Pha 2: Admin duyệt & xuất bản)
@router.post("/skills/publish")
async def publish_skill(req: PublishSkillRequest):
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    role = user_info["role"]
    
    if role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền xuất bản skill")
        
    valid_agents = ["hr_policies", "salary_management", "system_admin", "user_management"]
    if req.agent_id not in valid_agents:
        raise HTTPException(status_code=400, detail=f"Agent ID `{req.agent_id}` không hợp lệ")
        
    try:
        skill_data = req.skill_data
        
        # Parse cấu hình JSON đã duyệt ngược lại thành đối tượng Pydantic Skill
        published_skill = Skill(
            id=skill_data["id"],
            name=skill_data["name"],
            version=skill_data.get("version", "1.0.0"),
            description=skill_data["description"],
            skill_type=SkillType(skill_data["skill_type"]),
            parameters=[Parameter(**p) for p in skill_data.get("parameters", [])],
            system_prompt=skill_data["system_prompt"],
            permission=Permission(required_roles=skill_data.get("permission", {}).get("required_roles", [])),
            examples=skill_data.get("examples", []),
            metadata=skill_data.get("metadata", {}),
            created_at=datetime.now(),
            created_by=user_info["name"]
        )
        
        # Đăng ký vào registry bộ nhớ
        skill_registry.register(published_skill, [req.agent_id])
        
        # Kích hoạt trên agent đang chạy
        if req.agent_id == "hr_policies":
            hr_agent_with_skills.enable_skill(published_skill.id)
        elif req.agent_id == "salary_management":
            salary_agent_with_skills.enable_skill(published_skill.id)
        elif req.agent_id == "system_admin":
            system_admin_agent_with_skills.enable_skill(published_skill.id)
        elif req.agent_id == "user_management":
            user_management_agent_with_skills.enable_skill(published_skill.id)
            
        # Ghi tệp cấu hình JSON xuống ổ đĩa
        skill_file = os.path.join(settings.SKILLS_DIR, f"{published_skill.id}.json")
        os.makedirs(os.path.dirname(skill_file), exist_ok=True)
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(published_skill.model_dump_json(indent=4))
            
        return {
            "success": True,
            "skill": {
                "id": published_skill.id,
                "name": published_skill.name,
                "description": published_skill.description,
                "target_agent": req.agent_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất bản skill: {e}")

# API create new skill dynamically (Admin only)
@router.post("/create_skill")
async def create_skill(req: CreateSkillRequest):
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    role = user_info["role"]
    name = user_info["name"]
    
    if role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền tạo skill mới")
        
    valid_agents = ["hr_policies", "salary_management", "system_admin", "user_management"]
    if req.agent_id not in valid_agents:
        raise HTTPException(status_code=400, detail=f"Agent ID `{req.agent_id}` không hợp lệ")
        
    try:
        # Build using SkillFactory
        new_skill = await skill_factory.create_from_description(
            user_description=req.description,
            agent_id=req.agent_id,
            created_by=name
        )
        
        # Register
        skill_registry.register(new_skill, [req.agent_id])
        
        # Enable it in the active agent
        if req.agent_id == "hr_policies":
            hr_agent_with_skills.enable_skill(new_skill.id)
        elif req.agent_id == "salary_management":
            salary_agent_with_skills.enable_skill(new_skill.id)
        elif req.agent_id == "system_admin":
            system_admin_agent_with_skills.enable_skill(new_skill.id)
        elif req.agent_id == "user_management":
            user_management_agent_with_skills.enable_skill(new_skill.id)
            
        # Save to disk
        skill_file = os.path.join(settings.SKILLS_DIR, f"{new_skill.id}.json")
        os.makedirs(os.path.dirname(skill_file), exist_ok=True)
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(new_skill.model_dump_json(indent=4))
            
        return {
            "success": True,
            "skill": {
                "id": new_skill.id,
                "name": new_skill.name,
                "description": new_skill.description,
                "target_agent": req.agent_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo skill: {e}")

@router.delete("/delete_skill")
async def delete_skill(skill_id: str, user_id: str):
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    role = user_info["role"]
    
    if role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền xóa skill")
        
    # Check if skill exists
    skill = skill_registry.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy kỹ năng có ID {skill_id}")
        
    # Remove from registry
    skill_registry.remove(skill_id)
    
    # Disable from all active agent instances
    hr_agent_with_skills.disable_skill(skill_id)
    salary_agent_with_skills.disable_skill(skill_id)
    system_admin_agent_with_skills.disable_skill(skill_id)
    user_management_agent_with_skills.disable_skill(skill_id)
    
    # Delete from custom skills disk path if applicable
    skill_file = os.path.join(settings.SKILLS_DIR, f"{skill_id}.json")
    if os.path.exists(skill_file):
        try:
            os.remove(skill_file)
            print(f"🗑️ Deleted custom skill file: {skill_file}")
        except Exception as e:
            print(f"⚠️ Error deleting file: {e}")
            
    return {"success": True, "message": f"Đã xóa thành công kỹ năng {skill_id}"}


# ============================================================
# TOOL API ENDPOINTS
# ============================================================

@router.get("/tools")
async def get_tools():
    """Return all tools from the persistent store."""
    tools = tool_store.load_tools()
    return tools


@router.post("/tools")
async def create_tool(req: CreateToolRequest):
    """Create a new tool (admin only)."""
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền tạo tool mới")

    clean_id = req.id.strip().lower().replace(" ", "_")
    try:
        new_tool = tool_store.add_tool({
            "id": clean_id,
            "name": clean_id,
            "icon": req.icon,
            "description": req.description,
            "agent": req.agent,
            "category": req.category,
            "created_by": user_info["name"]
        })
        return {"success": True, "tool": new_tool}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/tools/{tool_id}")
async def update_tool(tool_id: str, req: UpdateToolRequest):
    """Update a tool (admin only). Supports toggling active, editing description/category/agent."""
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền cập nhật tool")

    updates = {}
    if req.active is not None:
        updates["active"] = req.active
    if req.description is not None:
        updates["description"] = req.description
    if req.category is not None:
        updates["category"] = req.category
    if req.agent is not None:
        updates["agent"] = req.agent

    try:
        updated_tool = tool_store.update_tool(tool_id, updates)
        return {"success": True, "tool": updated_tool}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/tools/{tool_id}")
async def delete_tool(tool_id: str, user_id: str = Query(...)):
    """Delete a tool (admin only)."""
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền xóa tool")

    try:
        tool_store.delete_tool(tool_id)
        return {"success": True, "message": f"Đã xóa thành công tool {tool_id}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================
# AGENT MANAGEMENT API ENDPOINTS
# ============================================================

@router.get("/agents/config")
async def get_agents_config(user_id: str = Query(...)):
    """Return full agent configs including system_prompt (admin only)."""
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được xem cấu hình agent")

    agents = agent_store.load_agents()
    return agents


@router.put("/agents/{agent_id}/prompt")
async def save_agent_prompt(agent_id: str, req: AgentPromptRequest):
    """Save the system prompt for an agent (admin only)."""
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền lưu prompt")

    try:
        agent_store.update_agent_prompt(agent_id, req.system_prompt)
        return {"success": True, "message": f"Đã lưu prompt cho Agent {agent_id}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/agents")
async def create_agent(req: CreateAgentRequest):
    """Create a new custom agent (admin only)."""
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền tạo agent")

    clean_id = req.id.strip().lower().replace(" ", "_")
    try:
        new_agent = agent_store.add_agent({
            "id": clean_id,
            "name": req.name,
            "icon": req.icon,
            "description": req.description,
            "welcome": req.welcome,
            "system_prompt": req.system_prompt,
            "created_by": user_info["name"]
        })
        return {"success": True, "agent": new_agent}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, user_id: str = Query(...)):
    """Delete a custom agent (admin only). Builtin agents cannot be deleted."""
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền xóa agent")

    try:
        agent_store.delete_agent(agent_id)
        return {"success": True, "message": f"Đã xóa thành công agent {agent_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
