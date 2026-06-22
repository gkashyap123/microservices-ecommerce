import { Navigate, Outlet } from "react-router-dom";
import { useSelector } from "react-redux";
import type { RootState } from "../../core/store/store";

export default function ProtectedRoute() {
  const isAuthenticated = useSelector(
    (s: RootState) => s.auth.isAuthenticated
  );
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}