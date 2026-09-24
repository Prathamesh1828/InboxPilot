"use client";

import { Suspense } from "react";
import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const TOKEN_KEY = "inboxpilot_token";

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

    // Save token to localStorage immediately
    localStorage.setItem(TOKEN_KEY, token);

    // Fetch the user profile using the new token
    refreshUser()
      .then(() => {
        router.replace("/dashboard");
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
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
