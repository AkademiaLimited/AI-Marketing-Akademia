"use client";

import { useEffect, useState, createContext, useContext, ReactNode } from "react";

type AuthUser = {
  id: string;
  email: string;
  name: string;
  is_superuser: boolean;
};

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
  error: string | null;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email, password }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Login failed: ${res.status}`);
      }
      const data = (await res.json()) as { access_token: string };
      setToken(data.access_token);
      const meRes = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      if (!meRes.ok) throw new Error("Could not verify admin account");
      const me = (await meRes.json()) as AuthUser;
      if (!me.is_superuser) throw new Error("Admin access required");
      sessionStorage.setItem("admin_token", data.access_token);
      setUser(me);
      setToken(data.access_token);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      setUser(null);
      setToken(null);
      sessionStorage.removeItem("admin_token");
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    sessionStorage.removeItem("admin_token");
  };

  useEffect(() => {
    const storedToken = sessionStorage.getItem("admin_token");
    if (!storedToken) {
      setLoading(false);
      return;
    }

    fetch(`${API_URL}/auth/me`, { headers: { Authorization: `Bearer ${storedToken}` } })
      .then(async (res) => {
        if (!res.ok) throw new Error("Session expired");
        const me = (await res.json()) as AuthUser;
        if (!me.is_superuser) throw new Error("Admin access required");
        setToken(storedToken);
        setUser(me);
      })
      .catch(() => {
        sessionStorage.removeItem("admin_token");
      })
      .finally(() => setLoading(false));
    }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
