import React, { useEffect } from "react";
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
    loadChats,
    createChat,
    selectChat,
    sendMessage,
    deleteChat,
  } = useChat();

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }
    loadChats();
  }, [isLoggedIn]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-white dark:bg-slate-950">
      <Sidebar
        chats={chats}
        selectedChatId={currentChat?.id || null}
        onSelectChat={selectChat}
        onNewChat={createChat}
        onDeleteChat={deleteChat}
        onLogout={handleLogout}
      />

      <div className="flex-1 flex flex-col">
        {currentChat ? (
          <>
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                {currentChat.title}
              </h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Model: {currentChat.model}
              </p>
            </div>
            <ChatWindow
              messages={messages}
              onSendMessage={sendMessage}
              loading={loading}
            />
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
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
