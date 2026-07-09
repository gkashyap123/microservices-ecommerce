import api from "../../core/api/axiosInstance";
import type { LoginRequest, RegisterRequest, TokenResponse, User } from "../../shared/types";

export const authService = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const res = await api.post("/auth/login", data);
    return res.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const res = await api.post("/auth/register", data);
    return res.data;
  },

  getMe: async (token?: string): Promise<User> => {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    const res = await api.get("/auth/me", config);
    return res.data;
  },
};