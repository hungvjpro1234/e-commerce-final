import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  first_name: string;
  last_name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setAuth: (user, token) => set({ user, token }),
      logout: () => set({ user: null, token: null }),
    }),
    {
      name: "auth-storage",
    }
  )
);
