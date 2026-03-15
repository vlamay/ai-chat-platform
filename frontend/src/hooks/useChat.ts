import { useState, useCallback } from "react";
import { chatsAPI } from "../api/chats";
import type { Chat, ChatListItem, Message } from "../types";

export const useChat = () => {
  const [chats, setChats] = useState<ChatListItem[]>([]);
  const [currentChat, setCurrentChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadChats = useCallback(async () => {
    try {
      setLoading(true);
      const data = await chatsAPI.listChats();
      setChats(data);
    } catch (err) {
      setError("Failed to load chats");
    } finally {
      setLoading(false);
    }
  }, []);

  const createChat = useCallback(async (title: string = "New Chat", model: string = "claude-haiku-4-5-20251001") => {
    try {
      setLoading(true);
      const chat = await chatsAPI.createChat(title, model);
      const chatItem: ChatListItem = {
        id: chat.id,
        title: chat.title,
        model: chat.model,
        created_at: chat.created_at,
        updated_at: chat.updated_at,
        message_count: 0,
      };
      setChats((prev) => [chatItem, ...prev]);
      setCurrentChat(chat);
      setMessages([]);
      return chat;
    } catch (err) {
      setError("Failed to create chat");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const selectChat = useCallback(async (chatId: string) => {
    try {
      setLoading(true);
      const chat = await chatsAPI.getChat(chatId);
      const msgs = await chatsAPI.getMessages(chatId);
      setCurrentChat(chat);
      setMessages(msgs);
    } catch (err) {
      setError("Failed to load chat");
    } finally {
      setLoading(false);
    }
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!currentChat) return;

      try {
        setLoading(true);
        // Add user message optimistically
        const userMessage: Message = {
          id: Date.now().toString(),
          chat_id: currentChat.id,
          role: "user",
          content,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, userMessage]);

        // Stream response
        const stream = await chatsAPI.streamMessage(currentChat.id, content);
        const reader = stream.getReader();
        let assistantContent = "";

        const decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const text = line.slice(6);
              assistantContent += text;
              // Update streaming message in real-time
              setMessages((prev) => {
                const updated = [...prev];
                const lastMsg = updated[updated.length - 1];
                if (lastMsg?.role === "assistant" && lastMsg?.id === "streaming") {
                  lastMsg.content = assistantContent;
                }
                return updated;
              });
            }
          }
        }

        // Add final assistant message
        const assistantMessage: Message = {
          id: Date.now().toString() + "1",
          chat_id: currentChat.id,
          role: "assistant",
          content: assistantContent,
          created_at: new Date().toISOString(),
        };

        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== "streaming");
          return [...filtered, assistantMessage];
        });
      } catch (err) {
        setError("Failed to send message");
      } finally {
        setLoading(false);
      }
    },
    [currentChat]
  );

  const deleteChat = useCallback(async (chatId: string) => {
    try {
      await chatsAPI.deleteChat(chatId);
      setChats((prev) => prev.filter((c) => c.id !== chatId));
      if (currentChat?.id === chatId) {
        setCurrentChat(null);
        setMessages([]);
      }
    } catch (err) {
      setError("Failed to delete chat");
    }
  }, [currentChat]);

  return {
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
  };
};
