import { Navigate, Outlet, useLocation } from "react-router-dom";
import type { UserRole } from "../../types/auth";
import { useAuth } from "../providers/AuthProvider";

interface RequireRoleProps {
  allowed: UserRole[];
}

export function RequireRole({ allowed }: RequireRoleProps) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!allowed.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
