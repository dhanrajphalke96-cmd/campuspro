import { useEffect, useMemo, useState } from 'react';
import api from '../../api/axios';

const STORAGE_KEY = (username) => `chatbot_session_${username}`;
const MESSAGE_KEY = (username) => `chatbot_messages_${username}`;

const promptsByRole = {
  student: [
    "What's my attendance?",
    'Any fees pending?',
    'Show my CGPA',
    "Library books I've issued",
  ],
  faculty: ['Show my subjects', 'Pending marks entry?', 'Apply for leave'],
  hod: ['Department attendance summary', 'Pending leave approvals'],
  admin: ['How to add a new student?', 'System module overview'],
  principal: ['Institution analytics summary', 'Student and staff overview'],
  accountant: ["Today's collection report", 'Pending dues summary'],
  hr: ['Pending leave requests', "This month's payroll status"],
  librarian: ['Books currently issued', 'Overdue book list'],
};

export default function useChatbot(role, username) {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!username) return;
    const storedSession = localStorage.getItem(STORAGE_KEY(username));
    const storedMessages = localStorage.getItem(MESSAGE_KEY(username));
    if (storedSession) setSessionId(storedSession);
    if (storedMessages) {
      try {
        setMessages(JSON.parse(storedMessages));
      } catch {
        setMessages([]);
      }
    }
  }, [username]);

  useEffect(() => {
    if (!username) return;
    if (sessionId) {
      localStorage.setItem(STORAGE_KEY(username), sessionId);
    }
  }, [sessionId, username]);

  useEffect(() => {
    if (!username) return;
    localStorage.setItem(MESSAGE_KEY(username), JSON.stringify(messages));
    const unreadCount = messages.filter((message) => message.role === 'assistant').length;
    setUnread(unreadCount);
  }, [messages, username]);

  const rolePrompts = useMemo(() => promptsByRole[role] || [], [role]);

  const sendMessage = async (message) => {
    setError(null);
    if (!message.trim()) return;

    const localMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, localMessage]);
    setLoading(true);

    try {
      const response = await api.post('chatbot/message/', {
        message,
        session_id: sessionId,
      });
      const assistant = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.data.reply,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistant]);
      setSessionId(response.data.session_id);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Unable to send chatbot message right now.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(null);
    setError(null);
    if (!username) return;
    localStorage.removeItem(STORAGE_KEY(username));
    localStorage.removeItem(MESSAGE_KEY(username));
  };

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearChat,
    sessionId,
    rolePrompts,
    unread,
  };
}
