"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const TOKEN_KEY = "inboxpilot_token";

/**
 * /auth/callback
 *
 * This page handles the redirect from the Google OAuth flow.
 * The backend redirects here with ?token=<jwt_token> after successful auth.
 *
 * Steps:
 * 1. Read the token from the URL search params.
 * 2. Save the token to localStorage.
 * 3. Call /auth/me to get the full user profile.
 * 4. Update the global auth state.
 * 5. Navigate to /dashboard.
 *
 * On any error, redirect to /login with an error message.
 */
export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser, login } = useAuth();

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

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-muted-foreground text-sm">Completing sign in...</p>
      </div>
    </div>
  );
}
