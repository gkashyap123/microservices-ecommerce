import axios from "axios";
import { store } from "../store/store";
import toast from "react-hot-toast";

const api = axios.create({
  baseURL: import.meta.env.VITE_GATEWAY_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// ── Request interceptor — attach JWT ──────────────────────────────────
api.interceptors.request.use((config) => {
  const token = store.getState().auth.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response interceptor — handle errors globally ─────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status  = error.response?.status;
    const message = error.response?.data?.detail ?? "Something went wrong";

    if (status === 401) {
      store.dispatch({ type: "auth/logout" });
      window.location.href = "/login";
      toast.error("Session expired — please login again");
    } else if (status === 429) {
      toast.error("Too many requests — please slow down");
    } else if (status >= 500) {
      toast.error("Server error — please try again later");
    } else {
      toast.error(message);
    }

    return Promise.reject(error);
  }
);

export default api;