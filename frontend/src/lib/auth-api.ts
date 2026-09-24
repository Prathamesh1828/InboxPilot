const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const defaultHeaders = {
  "Content-Type": "application/json",
};

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  return token ? { ...defaultHeaders, Authorization: `Bearer ${token}` } : defaultHeaders;
}

export const authApi = {
  async signup(data: any) {
    const res = await fetch(`${API_URL}/auth/signup`, {
      method: "POST",
      headers: defaultHeaders,
      credentials: "include",
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Failed to create account. Please try again.");
    }
    const user = await res.json();
    // Save token to localStorage for cross-domain auth
    if (user.access_token && typeof window !== "undefined") {
      localStorage.setItem("token", user.access_token);
    }
    return user;
  },

  async login(data: any) {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: defaultHeaders,
      credentials: "include",
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || "Incorrect email or password.");
    }
    const user = await res.json();
    // Save token to localStorage for cross-domain auth
    if (user.access_token && typeof window !== "undefined") {
      localStorage.setItem("token", user.access_token);
    }
    return user;
  },

  async logout() {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
        headers: getAuthHeaders(),
      });
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
      }
    }
  },

  async getMe() {
    const res = await fetch(`${API_URL}/auth/me`, {
      method: "GET",
      credentials: "include",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      throw new Error("Not authenticated");
    }
    return res.json();
  },
};
