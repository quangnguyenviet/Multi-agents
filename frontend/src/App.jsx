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

      const res = await fetch(`/api/user?user_id=${userId}`);
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

      // Fetch skills (catalog read-only)
      try {
        const skillsRes = await fetch("/api/skills");
        if (skillsRes.ok) {
          const skillsData = await skillsRes.json();
          setSkills(skillsData);
          addLog(`Loaded ${skillsData.length} skills from backend.`, "success");
        }
      } catch (skillsErr) {
        addLog(`Skill fetch failed: ${skillsErr.message}`, "warning");
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
        wordDownloadUrl: data.word_download_url || null,
        skillTag: "LangGraph Engine",
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
                          />
                        }
                      />
                      <Route
                        path="admin/tools"
                        element={
                          <ToolRegistry
                            activeTab="tab-tools"
                            tools={tools}
                          />
                        }
                      />
                    </>
                  )}

                  {/* Fallback inside dashboard */}
                  <Route path="*" element={<Navigate to="chat" replace />} />
                </Routes>
              </div>

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
