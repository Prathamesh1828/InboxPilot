"use client";

import { Suspense } from "react";
import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const TOKEN_KEY = "inboxpilot_token";
const AUTH_COOKIE = "auth_indicator";

function setAuthIndicatorCookie() {
  const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toUTCString();
  document.cookie = `${AUTH_COOKIE}=1; path=/; expires=${expires}; SameSite=Lax`;
}

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuth();

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      router.replace("/login?error=oauth_failed");
      return;
    }

    // 1. Save JWT to localStorage
    localStorage.setItem(TOKEN_KEY, token);
    // 2. Set indicator cookie so Next.js middleware allows /dashboard
    setAuthIndicatorCookie();

    // 3. Verify the token works by fetching user profile
    refreshUser()
      .then(() => {
        router.replace("/dashboard");
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
        document.cookie = `${AUTH_COOKIE}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
        router.replace("/login?error=oauth_failed");
      });
  }, [searchParams, refreshUser, router]);

  return null;
}

export default function AuthCallbackPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-muted-foreground text-sm">Completing sign in...</p>
      </div>
      <Suspense fallback={null}>
        <CallbackHandler />
      </Suspense>
    </div>
  );
}
