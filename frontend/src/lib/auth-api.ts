/**
 * auth-api.ts
 *
 * Cross-domain auth strategy (Vercel frontend + Render backend):
 *
 * 1. JWT stored in localStorage → sent as Bearer token on every backend request.
 * 2. A lightweight "auth_indicator" cookie set on vercel.app after login so
 *    the Next.js edge middleware can detect authentication for route protection.
 *    This cookie does NOT contain the JWT — it is just a boolean flag.
 * 3. Backend also sets an httpOnly SameSite=None cookie for defence-in-depth,
 *    but we don't rely on it for client-side auth state.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "inboxpilot_token";
const AUTH_COOKIE = "auth_indicator";

// ─── Cookie helpers (for the vercel.app-domain indicator cookie) ──────────────

function setAuthIndicatorCookie(): void {
  if (typeof document === "undefined") return;
  // Expires in 7 days, matches JWT expiry
  const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toUTCString();
  document.cookie = `${AUTH_COOKIE}=1; path=/; expires=${expires}; SameSite=Lax`;
}

function clearAuthIndicatorCookie(): void {
  if (typeof document === "undefined") return;
  document.cookie = `${AUTH_COOKIE}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax`;
}

// ─── Token helpers (localStorage) ─────────────────────────────────────────────

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

function saveToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  clearAuthIndicatorCookie();
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
  }

  return fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: "include", // Also send cookies (belt + suspenders)
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
    if (user.access_token) {
      saveToken(user.access_token);
      setAuthIndicatorCookie();
    }
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
    if (user.access_token) {
      saveToken(user.access_token);
      setAuthIndicatorCookie();   // ← makes Next.js middleware allow /dashboard
    }
    return user;
  },

  async logout() {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } catch {
      // Ignore network errors on logout
    } finally {
      clearToken(); // also clears auth_indicator cookie
    }
  },

  async getMe() {
    const res = await apiFetch("/auth/me");
    if (!res.ok) {
      const err: any = new Error("Failed to get profile");
      err.status = res.status;
      throw err;
    }
    return res.json();
  },
};
