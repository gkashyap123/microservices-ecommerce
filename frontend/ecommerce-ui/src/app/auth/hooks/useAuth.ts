import { useDispatch, useSelector } from "react-redux";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { authService } from "../services/authService";
import { setCredentials, logout } from "../../core/store/slices/authSlice";
import type { RootState } from "../../core/store/store";
import type { LoginRequest, RegisterRequest } from "../../shared/types";

export const useAuth = () => {
  const dispatch  = useDispatch();
  const navigate  = useNavigate();
  const auth      = useSelector((s: RootState) => s.auth);

  const loginMutation = useMutation({
    mutationFn: async (data: LoginRequest) => {
      const tokenRes = await authService.login(data);
      const user     = await authService.getMe();   // fetch user after token
      return { token: tokenRes.access_token, user };
    },
    onSuccess: ({ token, user }) => {
      dispatch(setCredentials({ token, user }));
      toast.success(`Welcome back, ${user.username}!`);
      navigate("/products");
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: () => {
      toast.success("Account created! Please login.");
      navigate("/login");
    },
  });

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
    toast.success("Logged out successfully");
  };

  return {
    ...auth,
    login:    loginMutation.mutate,
    register: registerMutation.mutate,
    logout:   handleLogout,
    isLoggingIn:    loginMutation.isPending,
    isRegistering:  registerMutation.isPending,
  };
};