import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { AuthUser, UserRole } from "../../types/auth";

interface AuthContextValue {
  user: AuthUser | null;
  loginAs: (role: UserRole) => void;
  logout: () => void;
  hasRole: (role: UserRole | UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const demoUsers: Record<UserRole, AuthUser> = {
  requester: {
    id: "demo-requester",
    name: "Riley Requester",
    email: "riley.requester@example.com",
    role: "requester"
  },
  agent: {
    id: "demo-agent",
    name: "Avery Agent",
    email: "avery.agent@example.com",
    role: "agent",
    teamId: "team-core"
  },
  admin: {
    id: "demo-admin",
    name: "Alex Admin",
    email: "alex.admin@example.com",
    role: "admin"
  }
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(demoUsers.agent);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    loginAs: (role) => setUser(demoUsers[role]),
    logout: () => setUser(null),
    hasRole: (roles) => {
      const list = Array.isArray(roles) ? roles : [roles];
      return Boolean(user && list.includes(user.role));
    }
  }), [user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
