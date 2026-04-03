import React, { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../store';
import { chatAPI } from '../services/api';
import {
  FiPlus, FiMessageSquare, FiSend, FiTrash2,
  FiEdit2, FiMoreVertical, FiCheck, FiX, FiCpu, FiUser
} from 'react-icons/fi';

function ChatPage() {
  const user = useAuthStore((state) => state.user);
  const [chats, setChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Rename state
  const [renamingId, setRenamingId] = useState(null);
  const [renameValue, setRenameValue] = useState('');
  const renameInputRef = useRef(null);

  // Context menu state
  const [menuOpenId, setMenuOpenId] = useState(null);
  const menuRef = useRef(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadChats();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Close context menu on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpenId(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus rename input when opened
  useEffect(() => {
    if (renamingId && renameInputRef.current) {
      renameInputRef.current.focus();
      renameInputRef.current.select();
    }
  }, [renamingId]);

  const loadChats = async () => {
    try {
      const response = await chatAPI.getSessions();
      setChats(response.data.chats);
    } catch (err) {
      setError('Failed to load chats');
    }
  };

  const createNewChat = async () => {
    try {
      const response = await chatAPI.createSession('New Chat');
      const newChat = response.data.chat;
      setChats([newChat, ...chats]);
      openChat(newChat);
    } catch (err) {
      setError('Failed to create chat');
      setTimeout(() => setError(''), 3000);
    }
  };

  const openChat = async (chat) => {
    if (renamingId) return; // Don't switch chat while renaming
    try {
      const response = await chatAPI.getChat(chat._id);
      setCurrentChat(response.data.chat);
      setMessages(response.data.chat.messages || []);
    } catch (err) {
      setError('Failed to open chat');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !currentChat) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const sentInput = input;
    setInput('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(currentChat._id, sentInput);
      setMessages(response.data.chat.messages || []);
      setCurrentChat(response.data.chat);
    } catch (err) {
      setError('Failed to send message');
      setMessages((prev) => prev.slice(0, -1));
      setTimeout(() => setError(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const deleteChat = async (chatId, e) => {
    e.stopPropagation();
    setMenuOpenId(null);
    try {
      await chatAPI.deleteChat(chatId);
      setChats((prev) => prev.filter((c) => c._id !== chatId));
      if (currentChat?._id === chatId) {
        setCurrentChat(null);
        setMessages([]);
      }
    } catch (err) {
      setError('Failed to delete chat');
      setTimeout(() => setError(''), 3000);
    }
  };

  const startRename = (chat, e) => {
    e.stopPropagation();
    setMenuOpenId(null);
    setRenamingId(chat._id);
    setRenameValue(chat.title);
  };

  const confirmRename = async (chatId, e) => {
    e?.stopPropagation();
    const trimmed = renameValue.trim();
    if (!trimmed) {
      cancelRename();
      return;
    }
    try {
      await chatAPI.updateChatTitle(chatId, trimmed);
      setChats((prev) =>
        prev.map((c) => (c._id === chatId ? { ...c, title: trimmed } : c))
      );
      if (currentChat?._id === chatId) {
        setCurrentChat((prev) => ({ ...prev, title: trimmed }));
      }
    } catch (err) {
      setError('Failed to rename chat');
      setTimeout(() => setError(''), 3000);
    } finally {
      setRenamingId(null);
      setRenameValue('');
    }
  };

  const cancelRename = (e) => {
    e?.stopPropagation();
    setRenamingId(null);
    setRenameValue('');
  };

  const handleRenameKeyDown = (e, chatId) => {
    if (e.key === 'Enter') confirmRename(chatId, e);
    if (e.key === 'Escape') cancelRename(e);
  };

  const formatTime = (ts) => {
    try {
      return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  const formatDate = (ts) => {
    try {
      const d = new Date(ts);
      const today = new Date();
      if (d.toDateString() === today.toDateString()) return 'Today';
      const yesterday = new Date(today);
      yesterday.setDate(today.getDate() - 1);
      if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
      return d.toLocaleDateString();
    } catch {
      return '';
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)] bg-gray-900 text-white">
      {/* ─── Sidebar ─── */}
      <div className="w-64 bg-gray-950 flex flex-col border-r border-gray-800">
        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={createNewChat}
            className="w-full bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-semibold py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all duration-200 shadow-lg shadow-blue-900/30"
          >
            <FiPlus size={18} /> New Chat
          </button>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto px-2 pb-2 space-y-1">
          {chats.length === 0 ? (
            <p className="text-center text-gray-500 text-sm mt-8">No chats yet</p>
          ) : (
            chats.map((chat) => (
              <div
                key={chat._id}
                onClick={() => openChat(chat)}
                className={`group relative w-full text-left rounded-xl cursor-pointer transition-all duration-150 ${
                  currentChat?._id === chat._id
                    ? 'bg-blue-600/20 border border-blue-500/40'
                    : 'hover:bg-gray-800 border border-transparent'
                }`}
              >
                {renamingId === chat._id ? (
                  /* ── Rename inline editor ── */
                  <div
                    className="flex items-center gap-1 p-2"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <input
                      ref={renameInputRef}
                      value={renameValue}
                      onChange={(e) => setRenameValue(e.target.value)}
                      onKeyDown={(e) => handleRenameKeyDown(e, chat._id)}
                      className="flex-1 bg-gray-700 text-white text-sm px-2 py-1 rounded-lg border border-blue-500 focus:outline-none"
                    />
                    <button
                      onClick={(e) => confirmRename(chat._id, e)}
                      className="text-green-400 hover:text-green-300 p-1"
                      title="Save"
                    >
                      <FiCheck size={14} />
                    </button>
                    <button
                      onClick={cancelRename}
                      className="text-gray-400 hover:text-gray-200 p-1"
                      title="Cancel"
                    >
                      <FiX size={14} />
                    </button>
                  </div>
                ) : (
                  /* ── Normal chat item ── */
                  <div className="flex items-center px-3 py-2.5">
                    <div className="flex-1 min-w-0">
                      <p className="truncate text-sm font-medium text-gray-100">
                        {chat.title}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {formatDate(chat.updated_at)}
                      </p>
                    </div>

                    {/* Three-dot menu button - visible on hover or when menu is open */}
                    <div className="relative" ref={menuOpenId === chat._id ? menuRef : null}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setMenuOpenId(menuOpenId === chat._id ? null : chat._id);
                        }}
                        className={`p-1 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700 transition-all ${
                          menuOpenId === chat._id
                            ? 'opacity-100 bg-gray-700'
                            : 'opacity-0 group-hover:opacity-100'
                        }`}
                        title="Options"
                      >
                        <FiMoreVertical size={15} />
                      </button>

                      {/* Dropdown Menu */}
                      {menuOpenId === chat._id && (
                        <div
                          className="absolute right-0 top-full mt-1 w-36 bg-gray-800 border border-gray-700 rounded-xl shadow-xl z-50 overflow-hidden"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <button
                            onClick={(e) => startRename(chat, e)}
                            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-200 hover:bg-gray-700 transition"
                          >
                            <FiEdit2 size={13} className="text-blue-400" />
                            Rename
                          </button>
                          <button
                            onClick={(e) => deleteChat(chat._id, e)}
                            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 transition"
                          >
                            <FiTrash2 size={13} />
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* ─── Main Chat Area ─── */}
      <div className="flex-1 flex flex-col bg-gray-900">
        {currentChat ? (
          <>
            {/* Header */}
            <div className="bg-gray-800/80 backdrop-blur border-b border-gray-700 px-6 py-3 flex items-center gap-3">
              <FiMessageSquare className="text-blue-400" size={18} />
              <h1 className="text-base font-semibold text-white truncate flex-1">
                {currentChat.title}
              </h1>
              <span className="text-xs text-gray-500">
                {messages.length} message{messages.length !== 1 ? 's' : ''}
              </span>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-500">
                    <FiMessageSquare size={40} className="mx-auto mb-3 opacity-40" />
                    <p className="text-sm">Send a message to start the conversation</p>
                  </div>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex gap-3 items-start ${
                      msg.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {msg.role === 'assistant' && (
                      <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 mt-1">
                        <FiCpu size={13} />
                      </div>
                    )}
                    <div
                      className={`max-w-[70%] px-4 py-3 rounded-2xl shadow-sm ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white rounded-tr-sm'
                          : 'bg-gray-800 text-gray-100 rounded-tl-sm border border-gray-700'
                      }`}
                    >
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                      <p className={`text-xs mt-1.5 ${msg.role === 'user' ? 'text-blue-200' : 'text-gray-500'} text-right`}>
                        {formatTime(msg.timestamp)}
                      </p>
                    </div>
                    {msg.role === 'user' && (
                      <div className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0 mt-1">
                        <FiUser size={13} />
                      </div>
                    )}
                  </div>
                ))
              )}

              {/* Typing indicator */}
              {loading && (
                <div className="flex gap-3 items-start justify-start">
                  <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <FiCpu size={13} />
                  </div>
                  <div className="bg-gray-800 border border-gray-700 px-4 py-3 rounded-2xl rounded-tl-sm">
                    <div className="flex gap-1.5 items-center">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form
              onSubmit={sendMessage}
              className="bg-gray-800/80 backdrop-blur border-t border-gray-700 p-4 flex gap-3"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 bg-gray-700 text-white placeholder-gray-400 px-4 py-2.5 rounded-xl border border-gray-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white px-5 py-2.5 rounded-xl flex items-center gap-2 font-medium transition-all duration-200"
              >
                <FiSend size={16} />
                Send
              </button>
            </form>
          </>
        ) : (
          /* Empty state */
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center gap-5 text-center">
              <div className="w-20 h-20 bg-blue-600/10 border border-blue-500/20 rounded-2xl flex items-center justify-center">
                <FiMessageSquare size={36} className="text-blue-400" />
              </div>
              <div>
                <p className="text-xl font-bold text-gray-200">Select a chat to start</p>
                <p className="text-gray-500 text-sm mt-1">Or create a new conversation</p>
              </div>
              <button
                onClick={createNewChat}
                className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-xl flex items-center gap-2 font-semibold transition-all duration-200 shadow-lg shadow-blue-900/30"
              >
                <FiPlus size={18} /> Create New Chat
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Error Toast */}
      {error && (
        <div className="fixed bottom-6 right-6 bg-red-500 text-white px-5 py-3 rounded-xl shadow-xl flex items-center gap-2 animate-fade-in">
          <FiX size={16} />
          {error}
        </div>
      )}
    </div>
  );
}

export default ChatPage;
