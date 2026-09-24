"use client";

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/auth-api";

interface User {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (userData: User) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  // Track if login() was called so we skip the initial getMe() race condition
  const justLoggedIn = useRef(false);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch {
      setUser(null);
      authApi.clearToken();
    }
  }, []);

  // On mount, restore session from backend using stored token
  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      // Skip the check if login() was already called (avoids race condition)
      if (!justLoggedIn.current) {
        await refreshUser();
      }
      setIsLoading(false);
    };
    init();
  }, []); // Run only once on mount

  /**
   * Called after a successful login API response.
   * Sets the user directly (no extra getMe() needed — we already have the user data).
   * Then navigates to the dashboard.
   */
  const login = useCallback((userData: User) => {
    justLoggedIn.current = true;
    setUser(userData);
    setIsLoading(false);
    router.push("/dashboard");
  }, [router]);

  const logout = useCallback(async () => {
    await authApi.logout();
    setUser(null);
    justLoggedIn.current = false;
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
        refreshUser,
      }}
    >
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
