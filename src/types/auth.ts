export type UserRole = "requester" | "agent" | "admin";

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  teamId?: string;
}
