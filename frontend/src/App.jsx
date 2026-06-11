import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, useParams } from 'react-router-dom';
import './App.css';

// Import Modular Components
import Toast from './components/common/Toast';
import Sidebar from './components/layout/Sidebar';
import LoginScreen from './components/login/LoginScreen';
import ChatWorkspace from './components/chat/ChatWorkspace';
import ConversationsPage from './components/chat/ConversationsPage';
import SkillManager from './components/admin/SkillManager';
import ToolRegistry from './components/admin/ToolRegistry';
import UserManager from './components/admin/UserManager';
import { apiFetch, apiRequestJson } from './api';

function createConversationId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }

  if (globalThis.crypto?.getRandomValues) {
    const bytes = globalThis.crypto.getRandomValues(new Uint8Array(16));
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    const hex = [...bytes].map(byte => byte.toString(16).padStart(2, '0'));
    return `${hex.slice(0, 4).join('')}-${hex.slice(4, 6).join('')}-${hex.slice(6, 8).join('')}-${hex.slice(8, 10).join('')}-${hex.slice(10).join('')}`;
  }

  return `conv-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

function ChatRoute({ currentUser, chatMessages, setChatMessages, conversationId, setConversationId, isTyping, handleSendMessage, addLog }) {
  const { convId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    if (!convId || !currentUser || convId === conversationId) return;

    setConversationId(convId);
    setChatMessages([]);

    apiRequestJson(`/api/conversations/${convId}/messages?user_id=${currentUser.id}`)
      .then(({ response, data }) => response.ok ? data : Promise.reject(new Error(data?.detail || 'Không nạp được hội thoại')))
      .then(data => {
        const msgs = (data.messages || []).map(m => ({
          role: m.role,
          text: m.text,
          agentName: m.role === 'assistant' ? 'AI Assistant' : undefined,
          avatarAbbr: m.role === 'assistant' ? 'AI' : undefined,
          timestamp: '',
        }));
        setChatMessages(msgs);
        addLog(`Loaded conversation ${convId}`, 'info');
      })
      .catch(err => addLog(`Load conversation error: ${err.message}`, 'error'));
  }, [convId]);

  return (
    <ChatWorkspace
      chatMessages={chatMessages}
      isTyping={isTyping}
      handleSendMessage={handleSendMessage}
      onBack={() => navigate('/chat')}
    />
  );
}

function App() {
  const navigate = useNavigate();

  /* GLOBAL STATES */
  const [currentUser, setCurrentUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('currentUser')) || null; } catch { return null; }
  });

  /* DYNAMIC REGISTRIES */
  const [skills, setSkills] = useState([]);
  const [tools, setTools] = useState([]);
  const [users, setUsers] = useState([]);

  /* CHAT STATES */
  const [chatMessages, setChatMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState(() => createConversationId());
  const [conversations, setConversations] = useState([]);

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

  /* SEED INITIAL LOGS + fetch data khi reload với user đã đăng nhập */
  useEffect(() => {
    addLog("LangGraph agent runtime compiled successfully.", "info");
    if (currentUser) {
      fetchConversations(currentUser.id);
      apiRequestJson("/api/tools").then(({ response, data }) => { if (response.ok && data.length) setTools(data); }).catch(() => {});
      apiRequestJson("/api/skills").then(({ response, data }) => { if (response.ok && data.length) setSkills(data); }).catch(() => {});
      if (currentUser.role === "admin") fetchUsers(currentUser.id);
    }
  }, []);

  /* LOGIN HANDLER — username + password */
  const handleLogin = async (username, password) => {
    try {
      addLog(`Authenticating: ${username}...`, "info");
      setConversationId(createConversationId());

      const { response: res, data } = await apiRequestJson("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) return data.detail || "Sai tên đăng nhập hoặc mật khẩu";

      const user = {
        id: data.user_id,
        username: data.username,
        name: data.name,
        role: data.role,
        avatar: data.name.split(" ").map(w => w[0]).join("").toUpperCase().substring(0, 2),
      };
      localStorage.setItem('currentUser', JSON.stringify(user));
      setCurrentUser(user);

      // Fetch tools
      try {
        const { response: toolsRes, data: d } = await apiRequestJson("/api/tools");
        if (toolsRes.ok) { setTools(d); addLog(`Loaded ${d.length} tools.`, "success"); }
      } catch (e) { addLog(`Tool fetch failed: ${e.message}`, "warning"); }

      // Fetch skills
      try {
        const { response: skillsRes, data: d } = await apiRequestJson("/api/skills");
        if (skillsRes.ok) { setSkills(d); addLog(`Loaded ${d.length} skills.`, "success"); }
      } catch (e) { addLog(`Skill fetch failed: ${e.message}`, "warning"); }

      // Fetch users nếu admin
      if (data.role === "admin") fetchUsers(data.user_id);

      fetchConversations(data.user_id);
      addLog(`Login completed! Role: ${data.role.toUpperCase()}`, "success");
      triggerToast(`Xin chào ${data.name}!`);
      return null; // không có lỗi
    } catch (err) {
      addLog(`Login Failed: ${err.message}`, "error");
      return err.message;
    }
  };

  /* FETCH danh sách users (admin) */
  const fetchUsers = async (adminId) => {
    try {
      const { response: res, data } = await apiRequestJson(`/api/users?user_id=${adminId}`);
      if (res.ok) setUsers(data);
    } catch (err) {
      addLog(`User list fetch failed: ${err.message}`, "warning");
    }
  };

  /* LOGOUT HANDLER */
  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    setCurrentUser(null);
    setChatMessages([]);
    setConversationId(createConversationId());
    setConversations([]);
    setSkills([]);
    setTools([]);
    setUsers([]);
    addLog(`User logged out from session`, "warning");
    navigate('/login');
  };

  /* NEW CHAT — bắt đầu cuộc trò chuyện mới (reset lịch sử backend qua conversation_id mới) */
  const handleNewChat = () => {
    const newId = createConversationId();
    setChatMessages([]);
    setConversationId(newId);
    addLog(`Started a new conversation`, "info");
    navigate('/chat/' + newId);
  };

  const handleStartChat = (initialText) => {
    const newId = createConversationId();
    setChatMessages([]);
    setConversationId(newId);
    navigate('/chat/' + newId);
    if (initialText) handleSendMessage(initialText, null, newId);
  };

  /* FETCH danh sách cuộc hội thoại của user */
  const fetchConversations = async (userId) => {
    try {
      const { response: res, data } = await apiRequestJson(`/api/conversations?user_id=${userId}`);
      if (res.ok) setConversations(data);
    } catch (err) {
      addLog(`Conversation list fetch failed: ${err.message}`, "warning");
    }
  };

  /* MỞ LẠI một cuộc hội thoại cũ — navigate đến route, ChatRoute tự load */
  const loadConversation = (id) => {
    navigate('/chat/' + id);
  };

  /* XÓA một cuộc hội thoại */
  const deleteConversation = async (id) => {
    if (!window.confirm("Xóa cuộc trò chuyện này khỏi hệ thống?")) return;
    try {
      const res = await apiFetch(`/api/conversations/${id}?user_id=${currentUser.id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error("Xóa thất bại");
      setConversations(prev => prev.filter(c => c.id !== id));
      if (id === conversationId) {
        setChatMessages([]);
        setConversationId(createConversationId());
        navigate('/chat');
      }
      triggerToast("Đã xóa cuộc trò chuyện!");
    } catch (err) {
      addLog(`Delete conversation error: ${err.message}`, "error");
      alert(`Lỗi xóa hội thoại: ${err.message}`);
    }
  };

  /* SEND CHAT MESSAGE & EXECUTE REAL-TIME LANGGRAPH WORKFLOW */
  const handleSendMessage = async (textToSend, file = null, overrideConvId = null) => {
    const text = textToSend.trim();
    if (!text && !file) return;

    const displayText = file ? (text ? `${text} 📄 ${file.name}` : `📄 ${file.name}`) : text;
    const userMsg = {
      role: "user",
      text: displayText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setChatMessages(prev => [...prev, userMsg]);
    addLog(`Sending query to LangGraph agent: "${text}"`, "info");
    setIsTyping(true);

    try {
      const formData = new FormData();
      formData.append('user_id', currentUser.id);
      formData.append('query', text || "");
      formData.append('conversation_id', overrideConvId || conversationId);
      if (file) formData.append('file', file);

      // Không set Content-Type — browser tự set multipart boundary
      const { response: res, data } = await apiRequestJson('/api/chat', { method: 'POST', body: formData });
      if (!res.ok) throw new Error(data.detail || "Chất lượng kết nối kém!");

      const botMsg = {
        role: "assistant",
        agentName: "AI Assistant",
        avatarAbbr: "AI",
        text: data.response,
        artifacts: data.artifacts || [],
        skillTag: data.skill_used || "LangGraph Engine",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setChatMessages(prev => [...prev, botMsg]);
      addLog(`Received response from LLM successfully`, "success");
      fetchConversations(currentUser.id);  // cập nhật danh sách (cuộc mới / thứ tự)
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
    return <LoginScreen handleLogin={handleLogin} />;
  }

  /* MAIN DASHBOARD RENDER WITH REACT ROUTER */
  return (
    <Routes>
      <Route path="/login" element={<LoginScreen handleLogin={handleLogin} />} />
      
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
                usersCount={users.length}
                handleLogout={handleLogout}
              />

              {/* 2. CENTER CONTENT SPACE */}
              <div className="content-panel">
                <Routes>
                  {/* Chat list */}
                  <Route
                    path="chat"
                    element={
                      <ConversationsPage
                        conversations={conversations}
                        onSelectConversation={loadConversation}
                        onDeleteConversation={deleteConversation}
                        onStartChat={handleStartChat}
                      />
                    }
                  />
                  {/* Chat room — URL phản ánh conversation_id để reload hoạt động */}
                  <Route
                    path="chat/:convId"
                    element={
                      <ChatRoute
                        currentUser={currentUser}
                        chatMessages={chatMessages}
                        setChatMessages={setChatMessages}
                        conversationId={conversationId}
                        setConversationId={setConversationId}
                        isTyping={isTyping}
                        handleSendMessage={handleSendMessage}
                        addLog={addLog}
                      />
                    }
                  />

                  {/* Admin-only paths */}
                  {currentUser.role === 'admin' && (
                    <>
                      <Route
                        path="admin/skills"
                        element={<SkillManager activeTab="tab-skills" skills={skills} />}
                      />
                      <Route
                        path="admin/tools"
                        element={<ToolRegistry activeTab="tab-tools" tools={tools} />}
                      />
                      <Route
                        path="admin/users"
                        element={
                          <UserManager
                            currentUser={currentUser}
                            users={users}
                            onRefresh={() => fetchUsers(currentUser.id)}
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
