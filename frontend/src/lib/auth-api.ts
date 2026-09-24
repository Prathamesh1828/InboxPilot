/**
 * auth-api.ts
 *
 * Handles all authentication API calls.
 *
 * Token Strategy (cross-domain Vercel + Render):
 * - Backend sets a SameSite=None; Secure cookie on login/signup.
 *   Modern browsers will send this cookie on cross-site requests.
 * - Backend ALSO returns the token in the JSON response body.
 *   We store this in localStorage as a fallback for cases where
 *   the cookie is blocked (e.g. Safari ITP, incognito).
 * - Every API request sends: credentials: "include" (for cookie)
 *   AND Authorization: Bearer <token> header (for localStorage fallback).
 * - The backend accepts both.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "inboxpilot_token";

// ─── Token helpers ────────────────────────────────────────────────────────────

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

function saveToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
}

// ─── Base fetch wrapper ───────────────────────────────────────────────────────

async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
    // Also set as a custom header for the Next.js middleware to read
    headers["x-auth-token"] = token;
  }

  return fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: "include", // Always send cookies too
  });
}

// ─── Auth API ─────────────────────────────────────────────────────────────────

export const authApi = {
  clearToken,

  async signup(data: { name: string; email: string; password: string }) {
    const res = await apiFetch("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to create account. Please try again.");
    }

    const user = await res.json();
    if (user.access_token) saveToken(user.access_token);
    return user;
  },

  async login(data: { email: string; password: string }) {
    const res = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Invalid email or password");
    }

    const user = await res.json();
    if (user.access_token) saveToken(user.access_token);
    return user;
  },

  async logout() {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } catch {
      // Ignore network errors on logout
    } finally {
      clearToken();
    }
  },

  async getMe() {
    const res = await apiFetch("/auth/me");
    if (!res.ok) {
      throw new Error("Not authenticated");
    }
    return res.json();
  },
};
