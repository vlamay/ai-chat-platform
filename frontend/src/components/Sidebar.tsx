import React from "react";
import type { ChatListItem } from "../types";

interface SidebarProps {
  chats: ChatListItem[];
  selectedChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  chats,
  selectedChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  onLogout,
}) => {
  return (
    <div className="w-64 bg-slate-100 dark:bg-slate-800 border-r border-slate-300 dark:border-slate-700
      flex flex-col h-full">
      {/* New Chat Button */}
      <div className="p-4 border-b border-slate-300 dark:border-slate-700">
        <button
          onClick={onNewChat}
          className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg
            font-medium transition"
        >
          + New Chat
        </button>
      </div>

      {/* Chats List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {chats.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-8">No chats yet</p>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.id}
              className={`group relative p-3 rounded-lg cursor-pointer transition ${
                selectedChatId === chat.id
                  ? "bg-blue-600 text-white"
                  : "bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-600"
              }`}
              onClick={() => onSelectChat(chat.id)}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{chat.title}</p>
                  <p className={`text-xs ${
                    selectedChatId === chat.id ? "text-blue-100" : "text-slate-500"
                  }`}>
                    {chat.message_count} messages
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 px-2 py-1 text-xs bg-red-600 hover:bg-red-700 text-white rounded transition"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Logout */}
      <div className="p-4 border-t border-slate-300 dark:border-slate-700">
        <button
          onClick={onLogout}
          className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition"
        >
          Logout
        </button>
      </div>
    </div>
  );
};
