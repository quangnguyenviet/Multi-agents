import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import './App.css';

// Import Modular Components
import Toast from './components/common/Toast';
import Sidebar from './components/layout/Sidebar';
import LoginScreen from './components/login/LoginScreen';
import ChatWorkspace from './components/chat/ChatWorkspace';
import AgentManager from './components/admin/AgentManager';
import SkillManager from './components/admin/SkillManager';
import ToolRegistry from './components/admin/ToolRegistry';
import AgentModal from './components/modals/AgentModal';
import ToolModal from './components/modals/ToolModal';
import SkillDraftModal from './components/modals/SkillDraftModal';


// Auto-route helper agent schema (Client-only classification trigger)
const AUTO_ROUTE_AGENT = {
  name: "✨ Tự động định tuyến (Router)",
  icon: "fa-route",
  description: "Hệ thống tự động phân loại ý định người dùng và chuyển tiếp đến Agent xử lý phù hợp nhất trong LangGraph.",
  welcome: "Xin chào! Tôi là **Router Tự động**. Hệ thống đang hoạt động ở chế độ phân phối thông minh. Bạn có thể hỏi bất kỳ câu hỏi nào về nhân sự, lương thưởng hoặc hệ thống, tôi sẽ tự động định tuyến đến Agent phù hợp nhất trong Graph!"
};

function App() {
  const navigate = useNavigate();

  /* GLOBAL STATES */
  const [currentUser, setCurrentUser] = useState(null); // { id, name, role, avatar }
  const [activeAgent, setActiveAgent] = useState("auto_route");

  /* DYNAMIC REGISTRIES */
  const [agents, setAgents] = useState({ auto_route: AUTO_ROUTE_AGENT });
  const [skills, setSkills] = useState([]);
  const [tools, setTools] = useState([]); // Visual catalog remains on FE

  /* CHAT STATES */
  const [chatMessages, setChatMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  /* MODALS STATES */
  const [agentModalOpen, setAgentModalOpen] = useState(false);
  const [toolModalOpen, setToolModalOpen] = useState(false);
  const [skillDraft, setSkillDraft] = useState(null); // Human-in-the-loop review state

  /* LIVE SYSTEM LOGS */
  const [systemLogs, setSystemLogs] = useState([]);
  const [sysCpu, setSysCpu] = useState("28%");
  const [sysRam, setSysRam] = useState("34%");

  /* TOAST NOTIFICATION */
  const [toast, setToast] = useState({ active: false, message: "" });

  /* TOAST HELPER */
  const triggerToast = (msg) => {
    setToast({ active: true, message: msg });
    setTimeout(() => {
      setToast({ active: false, message: "" });
    }, 3000);
  };

  /* TERMINAL LOGGER */
  const addLog = (message, type = 'info') => {
    const time = new Date();
    const timeStr = `[${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}:${String(time.getSeconds()).padStart(2, '0')}]`;
    const label = type.toUpperCase() + ":";
    const newLog = { time: timeStr, label, message, type };
    setSystemLogs(prev => [newLog, ...prev].slice(0, 25));
  };

  /* SEED INITIAL LOGS & SIMULATION TRAFFIC */
  useEffect(() => {
    addLog("GET /api/agents/status 200 OK", "success");
    addLog("Database ping response: 0.8ms", "success");
    addLog("Multi-Agent LangGraph runtime compiled successfully.", "info");

    const interval = setInterval(() => {
      const logsList = [
        { msg: "GET /api/agents/status 200 OK", type: "info" },
        { msg: "Database ping response: 0.9ms", type: "success" },
        { msg: "Memory Usage Warning: RAM hit 87.4 GB / 256 GB (34.1%)", type: "warning" },
        { msg: "Tool get_company_employee_list checked by system_admin", type: "info" },
        { msg: "Active LangGraph thread worker checked: 8/8 active", type: "success" }
      ];
      const randomLog = logsList[Math.floor(Math.random() * logsList.length)];
      addLog(randomLog.msg, randomLog.type);

      setSysCpu(`${Math.floor(Math.random() * 25) + 20}%`);
      setSysRam(`${Math.floor(Math.random() * 10) + 30}%`);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  /* SYNC INITIAL GREETINGS WHEN SWITCHING ACTIVE AGENT */
  useEffect(() => {
    if (!currentUser) return;
    const agent = agents[activeAgent];
    if (agent) {
      setChatMessages([
        {
          role: "assistant",
          agentName: agent.name,
          text: agent.welcome || "Xin chào! Tôi sẵn sàng hỗ trợ các câu hỏi của bạn.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      addLog(`Chat workspace switched active Agent target to: ${activeAgent}`, "info");
    }
  }, [activeAgent, currentUser, agents]);

  /* DYNAMIC SKILLS SYNC WHEN CHANGING ACTIVE AGENT */
  useEffect(() => {
    if (!currentUser || activeAgent === 'auto_route') {
      setSkills([]);
      return;
    }

    const fetchAgentSkills = async () => {
      try {
        addLog(`Fetching active skills for Agent: ${activeAgent} via API...`, "info");
        const res = await fetch(`/api/skills?agent_id=${activeAgent}&user_id=${currentUser.id}`);
        if (!res.ok) {
          throw new Error(`Failed to load skills: ${res.statusText}`);
        }
        const data = await res.json();
        // Backend returns skills as a flat list
        const formattedSkills = data.map(s => ({
          id: s.id,
          name: s.name,
          description: s.description,
          agent: activeAgent,
          category: "Live Agent Skill",
          active: true
        }));
        setSkills(formattedSkills);
        addLog(`Loaded ${data.length} skills successfully from backend.`, "success");
      } catch (err) {
        addLog(`Error fetching skills: ${err.message}`, "error");
      }
    };

    fetchAgentSkills();
  }, [activeAgent, currentUser]);

  /* DYNAMIC TOOLS SYNC ON COMPONENT LOAD */
  useEffect(() => {
    if (!currentUser) return;
    // Bind mock schemas representing backend Python tools
    const initialTools = [
      { id: "get_company_employee_list", name: "get_company_employee_list", icon: "fa-address-book", description: "Truy xuất danh sách toàn bộ nhân sự công ty bao gồm Mã nhân viên, Họ tên, Phòng ban và Vai trò.", agent: "system_admin", category: "Database Query", active: true },
      { id: "hr_policy_retriever", name: "hr_policy_retriever", icon: "fa-file-shield", description: "Tìm kiếm ngữ cảnh liên quan đến chính sách nhân sự trong cơ sở dữ liệu Vector (Chuyên dùng cho RAG).", agent: "hr_policies", category: "Vector Search", active: true },
      { id: "salary_calculator", name: "salary_calculator", icon: "fa-calculator", description: "Tính toán tổng thu nhập, khấu trừ bảo hiểm xã hội và thuế TNCN theo công thức lương mới nhất.", agent: "salary_management", category: "Math/Logic", active: true }
    ];
    setTools(initialTools);
  }, [currentUser]);

  /* QUICK LOGIN HANDLER (CONNECTS TO BACKEND AGENTS & PRIVILEGES) */
  const handleQuickLogin = async (userId) => {
    try {
      addLog(`Initiating secure authentication handshake for User ID: ${userId}...`, "info");
      const res = await fetch(`/api/agents?user_id=${userId}`);
      if (!res.ok) {
        throw new Error("Không thể kết nối đến máy chủ backend!");
      }
      const data = await res.json();
      console.log("Login API response data:", data);
      
      const loggedUser = {
        id: data.user_id,
        name: data.name,
        role: data.role,
        avatar: data.name.split(" ").map(w => w[0]).join("").toUpperCase().substring(0, 2)
      };
      
      setCurrentUser(loggedUser);

      // Build agents dictionary dynamically from backend schema
      const fetchedAgents = { auto_route: AUTO_ROUTE_AGENT };
      data.agents.forEach(a => {
        fetchedAgents[a.id] = {
          name: a.name,
          icon: a.icon,
          description: a.description,
          is_allowed: a.is_allowed,
          welcome: a.id === 'hr_policies' 
            ? "Chào bạn! Tôi là **HR Policies Agent**. Tôi chịu trách nhiệm giải đáp các thông tin chính thức liên quan đến: Quy chế công sở, Giờ giấc làm việc, và Ngày nghỉ phép."
            : a.id === 'salary_management'
            ? "Xin chào! Tôi là **Salary Management Agent**. Tôi có thể hỗ trợ tra cứu lương của bạn, tính toán thưởng Tết và kết xuất báo cáo lương công ty dành cho Quản lý."
            : "Kết nối hạ tầng Dell PowerEdge R750. Tôi là **System Admin Agent**, sẵn sàng hỗ trợ kiểm tra tài nguyên CPU, RAM, dung lượng SSD và đọc logs máy chủ."
        };
      });

      setAgents(fetchedAgents);
      addLog(`Secure login completed! User role: ${data.role.toUpperCase()}`, "success");
      triggerToast(`Đăng nhập thành công với vai trò ${data.role.toUpperCase()}!`);
    } catch (err) {
      addLog(`Login Failed: ${err.message}`, "error");
      alert(`Đăng nhập thất bại: ${err.message}`);
    }
  };

  /* LOGOUT HANDLER */
  const handleLogout = () => {
    setCurrentUser(null);
    setActiveAgent("auto_route");
    setAgents({ auto_route: AUTO_ROUTE_AGENT });
    setChatMessages([]);
    setSkills([]);
    addLog(`User logged out from session`, "warning");
    navigate('/login');
  };

  /* SAVE SYSTEM PROMPT */
  const saveSystemPrompt = (key, text) => {
    if (!text.trim()) {
      alert("Prompt không được để trống!");
      return;
    }
    // Update locally. In subsequent phase, connect to backend persist API if available
    setAgents(prev => ({
      ...prev,
      [key]: { ...prev[key], system_prompt: text }
    }));
    addLog(`Successfully updated local system instruction for Agent [${key}]: "${text.substring(0, 45)}..."`, "success");
    triggerToast(`Đã cập nhật prompt thành công cho ${agents[key]?.name}!`);
  };

  /* CREATE DYNAMIC AGENT (LOCAL GRAPH NODE REGISTER) */
  const handleCreateAgent = (agentData) => {
    const { id, name, icon, description, welcome, system_prompt } = agentData;
    const cleanId = id.trim().toLowerCase().replace(/\s+/g, '_');
    setAgents(prev => ({
      ...prev,
      [cleanId]: { name, icon, description, welcome, system_prompt, is_allowed: true }
    }));
    addLog(`CREATED AGENT: Dynamically registered [${name}] (ID: ${cleanId}) to LLM Graph.`, "success");
    triggerToast(`Đã tạo và kích hoạt thành công Agent: ${name}!`);
  };

  /* TOGGLE TOOL ACTIVE STATUS */
  const toggleToolStatus = (toolId) => {
    setTools(prev => prev.map(t => {
      if (t.id === toolId) {
        const nextActive = !t.active;
        addLog(`Tool [${toolId}] set to ${nextActive ? "ACTIVATED" : "DEACTIVATED"}`, nextActive ? "success" : "warning");
        triggerToast(`Đã ${nextActive ? 'kích hoạt' : 'tắt'} Tool ${toolId} thành công!`);
        return { ...t, active: nextActive };
      }
      return t;
    }));
  };

  /* DELETE TOOL */
  const deleteTool = (toolId) => {
    if (window.confirm(`Bạn có chắc chắn muốn xóa tool ${toolId}?`)) {
      setTools(prev => prev.filter(t => t.id !== toolId));
      addLog(`Deleted Tool calling schema: ${toolId}`, "warning");
      triggerToast(`Đã xóa tool ${toolId} thành công!`);
    }
  };

  /* CREATE DYNAMIC TOOL */
  const handleCreateTool = (toolData) => {
    const { id, icon, description, agent, category } = toolData;
    const cleanId = id.trim().toLowerCase().replace(/\s+/g, '_');
    const toolObj = {
      id: cleanId,
      name: cleanId,
      icon: icon || "fa-globe",
      description: description || "Mô tả tác vụ mặc định của tool gọi ngoài.",
      agent,
      category,
      active: true
    };
    setTools(prev => [...prev, toolObj]);
    addLog(`[REGISTERED TOOL] New tool calling schema registered: ${cleanId}`, "success");
    triggerToast(`Đăng ký và liên kết Tool ${cleanId} thành công!`);
  };

  /* DELETE SKILL VIA BACKEND API */
  const deleteSkill = async (skillId) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa kỹ năng ${skillId} khỏi hệ thống và ổ đĩa backend?`)) {
      return;
    }
    try {
      addLog(`Sending request to delete custom skill file: ${skillId}...`, "info");
      const res = await fetch(`/api/delete_skill?skill_id=${skillId}&user_id=${currentUser.id}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to delete skill");
      }
      setSkills(prev => prev.filter(s => s.id !== skillId));
      addLog(`[SKILL DELETED] Successfully deleted skill file: ${skillId}`, "success");
      triggerToast(`Đã xóa kỹ năng ${skillId} thành công!`);
    } catch (err) {
      addLog(`Error deleting skill: ${err.message}`, "error");
      alert(`Lỗi khi xóa kỹ năng: ${err.message}`);
    }
  };

  /* START SKILL DRAFT COMPILATION VIA BACKEND AI STUDIO API */
  const handleStartSkillDraft = async (name, description, agent) => {
    try {
      addLog(`Submitting natural language description for AI skill drafting...`, "info");
      const res = await fetch('/api/skills/draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          agent_id: agent,
          description: description
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to draft skill");
      }
      setSkillDraft(data.skill);
      addLog(`[HITL STAGE] Compiled AI prompt draft successfully for skill: ${name}`, "success");
    } catch (err) {
      addLog(`Error drafting skill: ${err.message}`, "error");
      alert(`Lỗi biên dịch nháp: ${err.message}`);
    }
  };

  /* PUBLISH SKILL AFTER HITL APPROVAL VIA BACKEND DYNAMIC ENGINE */
  const handlePublishSkill = async () => {
    if (!skillDraft) return;
    try {
      addLog(`Publishing dynamic skill to database and disk configurations...`, "info");
      const targetAgentId = skillDraft.metadata?.agent_id || activeAgent;
      
      const res = await fetch('/api/skills/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          agent_id: targetAgentId,
          skill_data: skillDraft
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to publish skill");
      }
      
      // Update local skills registry list dynamically
      const newSkillObj = {
        id: data.skill.id,
        name: data.skill.name,
        description: data.skill.description,
        agent: data.skill.target_agent,
        category: "AI Published",
        active: true
      };
      setSkills(prev => [...prev, newSkillObj]);
      addLog(`[SKILL PUBLISHED] Successfully compiled custom skill JSON: ${data.skill.id}`, "success");
      triggerToast(`Đăng ký & xuất bản Kỹ năng ${data.skill.name} thành công!`);
      setSkillDraft(null);
    } catch (err) {
      addLog(`Error publishing skill: ${err.message}`, "error");
      alert(`Lỗi xuất bản kỹ năng: ${err.message}`);
    }
  };

  /* SEND CHAT MESSAGE & EXECUTE REAL-TIME LANGGRAPH WORKFLOW */
  const handleSendMessage = async (textToSend) => {
    const text = textToSend.trim();
    if (!text) return;

    // Append User message locally
    const userMsg = {
      role: "user",
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setChatMessages(prev => [...prev, userMsg]);
    addLog(`Sending query to LangGraph Multi-Agent Engine: "${text}"`, "info");
    setIsTyping(true);

    try {
      // POST request to actual FastAPI router
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          active_agent: activeAgent, // 'auto_route', 'hr_policies', etc.
          query: text
        })
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Chất lượng kết nối kém!");
      }

      const routedAgentKey = data.target_agent;
      const targetAgentObj = agents[routedAgentKey] || { name: routedAgentKey };

      // Build abbreviations
      let avatarAbbr = "AG";
      if (targetAgentObj.name) {
        const words = targetAgentObj.name.split(" ");
        if (words.length >= 2) {
          avatarAbbr = (words[0][0] + words[1][0]).toUpperCase();
        } else {
          avatarAbbr = words[0].substring(0, 2).toUpperCase();
        }
      }

      // Check whether AI classified intent in Auto-routing
      let routeInfoBadge = "";
      if (activeAgent === 'auto_route' && routedAgentKey !== 'auto_route' && routedAgentKey !== 'unknown') {
        addLog(`[Router] Classified intent. Dynamic routed query to: ${routedAgentKey}`, "warning");
        routeInfoBadge = `Định tuyến thông minh: → ${targetAgentObj.name}`;
      }

      const botMsg = {
        role: "assistant",
        agentName: targetAgentObj.name || "AI Agent Response",
        avatarAbbr,
        text: data.response,
        skillTag: data.access_granted ? "LangGraph Engine" : "Access Denied",
        routeInfoBadge,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setChatMessages(prev => [...prev, botMsg]);
      addLog(`Received real response from Agent [${routedAgentKey}] successfully`, "success");
    } catch (err) {
      addLog(`Chat Error: ${err.message}`, "error");
      
      const errMsg = {
        role: "assistant",
        agentName: "Error Handler Node",
        avatarAbbr: "ER",
        text: `❌ **LỖI KẾT NỐI HỆ THỐNG:** Không thể kết nối với máy chủ AI Backend. Chi tiết lỗi: *"${err.message}"*. Vui lòng kiểm tra lại trạng thái Uvicorn Server.`,
        skillTag: "system_error",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setChatMessages(prev => [...prev, errMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  /* RENDER LOGIN IF NOT LOGGED IN */
  if (!currentUser) {
    return <LoginScreen handleQuickLogin={handleQuickLogin} />;
  }

  /* MAIN DASHBOARD RENDER WITH REACT ROUTER */
  return (
    <Routes>
      <Route path="/login" element={<LoginScreen handleQuickLogin={handleQuickLogin} />} />
      
      {/* Route Guard: Checks if user is logged in, redirects to /login if not */}
      <Route 
        path="/*" 
        element={
          currentUser ? (
            <div className="dashboard-container visible">
              {/* Background blobs */}
              <div className="bg-glow-container">
                <div className="bg-blob blob1"></div>
                <div className="bg-blob blob2"></div>
              </div>

              {/* 1. LEFT SIDEBAR */}
              <Sidebar 
                currentUser={currentUser}
                agentsCount={Object.keys(agents).length - 1} // Exclude auto_route from count
                skillsCount={skills.length}
                toolsCount={tools.length}
                handleLogout={handleLogout}
              />

              {/* 2. CENTER CONTENT SPACE */}
              <div className="content-panel">
                <Routes>
                  {/* Chat tab */}
                  <Route 
                    path="chat" 
                    element={
                      <ChatWorkspace 
                        activeTab="tab-chat"
                        activeAgent={activeAgent}
                        setActiveAgent={setActiveAgent}
                        agents={agents}
                        chatMessages={chatMessages}
                        isTyping={isTyping}
                        handleSendMessage={handleSendMessage}
                      />
                    } 
                  />

                  {/* Admin-only paths */}
                  {currentUser.role === 'admin' && (
                    <>
                      <Route 
                        path="admin/agents" 
                        element={
                          <AgentManager 
                            activeTab="tab-agents"
                            agents={agents}
                            saveSystemPrompt={saveSystemPrompt}
                            setAgentModalOpen={setAgentModalOpen}
                          />
                        } 
                      />
                      <Route 
                        path="admin/skills" 
                        element={
                          <SkillManager 
                            activeTab="tab-skills"
                            skills={skills}
                            agents={agents}
                            deleteSkill={deleteSkill}
                            onStartSkillDraft={handleStartSkillDraft}
                          />
                        } 
                      />
                      <Route 
                        path="admin/tools" 
                        element={
                          <ToolRegistry 
                            activeTab="tab-tools"
                            tools={tools}
                            agents={agents}
                            toggleToolStatus={toggleToolStatus}
                            deleteTool={deleteTool}
                            setToolModalOpen={setToolModalOpen}
                          />
                        } 
                      />
                    </>
                  )}

                  {/* Fallback inside dashboard */}
                  <Route path="*" element={<Navigate to="chat" replace />} />
                </Routes>
              </div>

              {/* 4. MODALS OVERLAYS */}
              <AgentModal 
                isOpen={agentModalOpen}
                onClose={() => setAgentModalOpen(false)}
                onCreateAgent={handleCreateAgent}
              />

              <ToolModal 
                isOpen={toolModalOpen}
                onClose={() => setToolModalOpen(false)}
                agents={agents}
                onCreateTool={handleCreateTool}
              />

              <SkillDraftModal 
                skillDraft={skillDraft}
                setSkillDraft={setSkillDraft}
                onPublishSkill={handlePublishSkill}
              />

              {/* TOAST NOTIFICATION POPUP */}
              <Toast active={toast.active} message={toast.message} />
            </div>
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  );
}

export default App;
