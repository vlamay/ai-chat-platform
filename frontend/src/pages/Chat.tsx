import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { useChat } from "../hooks/useChat";
import { Sidebar } from "../components/Sidebar";
import { ChatWindow } from "../components/ChatWindow";

export const Chat: React.FC = () => {
  const navigate = useNavigate();
  const { isLoggedIn, logout } = useAuthStore();
  const {
    chats,
    currentChat,
    messages,
    loading,
    error,
    loadChats,
    createChat,
    selectChat,
    sendMessage,
    deleteChat,
  } = useChat();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }
    loadChats();
  }, [isLoggedIn, navigate, loadChats]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-white dark:bg-slate-950">
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 transform transition-transform md:relative md:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <Sidebar
          chats={chats}
          selectedChatId={currentChat?.id || null}
          onSelectChat={(chatId) => {
            selectChat(chatId);
            setSidebarOpen(false);
          }}
          onNewChat={createChat}
          onDeleteChat={deleteChat}
          onLogout={handleLogout}
          loading={loading}
        />
      </div>

      <div className="flex-1 flex flex-col">
        {/* Error Banner */}
        {error && (
          <div className="bg-red-100 dark:bg-red-900 border-b border-red-300 dark:border-red-700 p-4">
            <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Mobile Menu Button & Header */}
        {currentChat ? (
          <>
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="md:hidden text-slate-900 dark:text-white text-xl"
                >
                  ☰
                </button>
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                    {currentChat.title}
                  </h2>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    Model: {currentChat.model}
                  </p>
                </div>
              </div>
            </div>
            <ChatWindow
              messages={messages}
              onSendMessage={sendMessage}
              loading={loading}
            />
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden absolute top-4 left-4 text-slate-900 dark:text-white text-xl"
            >
              ☰
            </button>
            <div className="text-center">
              <p className="text-2xl text-slate-600 dark:text-slate-400 mb-4">
                No chat selected
              </p>
              <button
                onClick={() => createChat()}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
              >
                Create New Chat
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
