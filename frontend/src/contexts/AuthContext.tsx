"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { authApi } from "@/lib/auth-api";

interface User {
  id: string;
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (userData: User) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const checkAuth = async () => {
      // If we already have a user (e.g. just logged in), skip the check
      if (user) {
        setIsLoading(false);
        return;
      }
      try {
        const userData = await authApi.getMe();
        setUser(userData);
      } catch (error) {
        setUser(null);
        // Only redirect to login if we're on a protected route
        const protectedRoutes = ["/dashboard", "/inbox", "/approvals", "/audit", "/settings", "/integrations"];
        if (protectedRoutes.some(r => pathname?.startsWith(r))) {
          router.push("/login");
        }
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();
  }, []); // Only run once on mount

  const login = (userData: User) => {
    setUser(userData);
    setIsLoading(false);
    router.push("/dashboard");
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
