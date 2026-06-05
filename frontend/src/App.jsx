import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import './App.css';

// Import Modular Components
import Toast from './components/common/Toast';
import Sidebar from './components/layout/Sidebar';
import LoginScreen from './components/login/LoginScreen';
import ChatWorkspace from './components/chat/ChatWorkspace';
import SkillManager from './components/admin/SkillManager';
import ToolRegistry from './components/admin/ToolRegistry';
import ToolModal from './components/modals/ToolModal';
import SkillDraftModal from './components/modals/SkillDraftModal';
import CVProcessor from './components/cv/CVProcessor';


function App() {
  const navigate = useNavigate();

  /* GLOBAL STATES */
  const [currentUser, setCurrentUser] = useState(null); // { id, name, role, avatar }

  /* DYNAMIC REGISTRIES */
  const [skills, setSkills] = useState([]);
  const [tools, setTools] = useState([]);

  /* CHAT STATES */
  const [chatMessages, setChatMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  /* MODALS STATES */
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

  /* SEED INITIAL LOGS */
  useEffect(() => {
    addLog("Multi-Agent LangGraph runtime compiled successfully.", "info");
  }, []);

  /* QUICK LOGIN HANDLER */
  const handleQuickLogin = async (userId) => {
    try {
      addLog(`Authenticating User ID: ${userId}...`, "info");

      const res = await fetch(`/api/agents?user_id=${userId}`);
      if (!res.ok) throw new Error("Không thể kết nối đến máy chủ backend!");
      const data = await res.json();

      setCurrentUser({
        id: data.user_id,
        name: data.name,
        role: data.role,
        avatar: data.name.split(" ").map(w => w[0]).join("").toUpperCase().substring(0, 2)
      });

      // Fetch tools
      try {
        const toolsRes = await fetch("/api/tools");
        if (toolsRes.ok) {
          const toolsData = await toolsRes.json();
          setTools(toolsData);
          addLog(`Loaded ${toolsData.length} tools from backend.`, "success");
        }
      } catch (toolsErr) {
        addLog(`Tool fetch failed: ${toolsErr.message}`, "warning");
      }

      addLog(`Login completed! Role: ${data.role.toUpperCase()}`, "success");
      triggerToast(`Đăng nhập thành công với vai trò ${data.role.toUpperCase()}!`);
    } catch (err) {
      addLog(`Login Failed: ${err.message}`, "error");
      alert(`Đăng nhập thất bại: ${err.message}`);
    }
  };

  /* LOGOUT HANDLER */
  const handleLogout = () => {
    setCurrentUser(null);
    setChatMessages([]);
    setSkills([]);
    setTools([]);
    addLog(`User logged out from session`, "warning");
    navigate('/login');
  };

  /* TOGGLE TOOL ACTIVE STATUS VIA BACKEND API */
  const toggleToolStatus = async (toolId) => {
    const tool = tools.find(t => t.id === toolId);
    if (!tool) return;
    const nextActive = !tool.active;
    try {
      const res = await fetch(`/api/tools/${toolId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: currentUser.id, active: nextActive })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to toggle tool");
      }
      setTools(prev => prev.map(t => t.id === toolId ? { ...t, active: nextActive } : t));
      addLog(`Tool [${toolId}] set to ${nextActive ? "ACTIVATED" : "DEACTIVATED"}`, nextActive ? "success" : "warning");
      triggerToast(`Đã ${nextActive ? 'kích hoạt' : 'tắt'} Tool ${toolId} thành công!`);
    } catch (err) {
      addLog(`Error toggling tool: ${err.message}`, "error");
      alert(`Lỗi cập nhật tool: ${err.message}`);
    }
  };

  /* DELETE TOOL VIA BACKEND API */
  const deleteTool = async (toolId) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa tool ${toolId}?`)) return;
    try {
      const res = await fetch(`/api/tools/${toolId}?user_id=${currentUser.id}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to delete tool");
      }
      setTools(prev => prev.filter(t => t.id !== toolId));
      addLog(`Deleted Tool calling schema: ${toolId}`, "warning");
      triggerToast(`Đã xóa tool ${toolId} thành công!`);
    } catch (err) {
      addLog(`Error deleting tool: ${err.message}`, "error");
      alert(`Lỗi xóa tool: ${err.message}`);
    }
  };

  /* CREATE DYNAMIC TOOL VIA BACKEND API */
  const handleCreateTool = async (toolData) => {
    const { id, icon, description, agent, category } = toolData;
    const cleanId = id.trim().toLowerCase().replace(/\s+/g, '_');
    try {
      addLog(`Creating tool [${cleanId}] via API...`, "info");
      const res = await fetch('/api/tools', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          id: cleanId,
          icon: icon || "fa-globe",
          description: description || "Mô tả tác vụ mặc định của tool gọi ngoài.",
          agent,
          category
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to create tool");
      }
      const created = data.tool;
      setTools(prev => [...prev, created]);
      addLog(`[REGISTERED TOOL] New tool calling schema registered: ${cleanId}`, "success");
      triggerToast(`Đăng ký và liên kết Tool ${cleanId} thành công!`);
    } catch (err) {
      addLog(`Error creating tool: ${err.message}`, "error");
      alert(`Lỗi tạo tool: ${err.message}`);
    }
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
      const targetAgentId = skillDraft.metadata?.agent_id || 'default';

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
  const handleSendMessage = async (textToSend, file = null) => {
    const text = textToSend.trim();
    if (!text && !file) return;

    const displayText = file ? `${text || "Tạo CV mới"} 📄 ${file.name}` : text;
    const userMsg = {
      role: "user",
      text: displayText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setChatMessages(prev => [...prev, userMsg]);
    addLog(`Sending query to LangGraph Multi-Agent Engine: "${text}"`, "info");
    setIsTyping(true);

    try {
      const formData = new FormData();
      formData.append('user_id', currentUser.id);
      formData.append('query', text || "Tạo CV mới cho tôi");
      if (file) formData.append('file', file);

      // Không set Content-Type — browser tự set multipart boundary
      const res = await fetch('/api/chat', { method: 'POST', body: formData });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Chất lượng kết nối kém!");

      const botMsg = {
        role: "assistant",
        agentName: "AI Assistant",
        avatarAbbr: "AI",
        text: data.response,
        cvHtml: data.cv_html || null,
        skillTag: data.cv_html ? "CV Generator" : "LangGraph Engine",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setChatMessages(prev => [...prev, botMsg]);
      addLog(`Received response from LLM successfully`, "success");
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
                        path="admin/skills"
                        element={
                          <SkillManager
                            activeTab="tab-skills"
                            skills={skills}
                            agents={{}}
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
                            agents={{}}
                            toggleToolStatus={toggleToolStatus}
                            deleteTool={deleteTool}
                            setToolModalOpen={setToolModalOpen}
                          />
                        }
                      />
                    </>
                  )}

                  {/* CV Processor — available to all logged-in users */}
                  <Route path="cv-processor" element={<CVProcessor />} />

                  {/* Fallback inside dashboard */}
                  <Route path="*" element={<Navigate to="chat" replace />} />
                </Routes>
              </div>

              {/* 4. MODALS OVERLAYS */}
              <ToolModal
                isOpen={toolModalOpen}
                onClose={() => setToolModalOpen(false)}
                agents={{}}
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
