import apiClient from "./client";
import { Chat, ChatListItem, Message } from "../types";

export const chatsAPI = {
  createChat: async (title: string, model: string): Promise<Chat> => {
    const response = await apiClient.post("/chats", { title, model });
    return response.data;
  },

  listChats: async (): Promise<ChatListItem[]> => {
    const response = await apiClient.get("/chats");
    return response.data;
  },

  getChat: async (chatId: string): Promise<Chat> => {
    const response = await apiClient.get(`/chats/${chatId}`);
    return response.data;
  },

  updateChat: async (chatId: string, title: string, model: string): Promise<Chat> => {
    const response = await apiClient.patch(`/chats/${chatId}`, { title, model });
    return response.data;
  },

  deleteChat: async (chatId: string): Promise<void> => {
    await apiClient.delete(`/chats/${chatId}`);
  },

  getMessages: async (chatId: string): Promise<Message[]> => {
    const response = await apiClient.get(`/messages/${chatId}`);
    return response.data;
  },

  streamMessage: async (chatId: string, content: string): Promise<ReadableStream> => {
    const response = await fetch(`${apiClient.defaults.baseURL}/messages/${chatId}/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
      },
      body: JSON.stringify({ content }),
    });
    return response.body!;
  },
};
