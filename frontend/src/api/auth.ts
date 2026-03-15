import apiClient from "./client";
import { TokenResponse } from "../types";

export const authAPI = {
  register: async (email: string, name: string, password: string): Promise<TokenResponse> => {
    const response = await apiClient.post("/auth/register", {
      email,
      name,
      password,
    });
    return response.data;
  },

  login: async (email: string, password: string): Promise<TokenResponse> => {
    const response = await apiClient.post("/auth/login", {
      email,
      password,
    });
    return response.data;
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },
};
