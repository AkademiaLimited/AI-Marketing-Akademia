"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../_components/auth-context";

export default function LoginPage() {
  const { login, loading, error } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (await login(email, password)) {
      router.push("/admin/dashboard");
    }
  };

  return (
    <main className="admin-login-page">
      <section className="admin-login-brand" aria-label="AI Marketer admin">
        <Link href="/" className="admin-login-logo">
          <span className="admin-login-mark">AM</span>
          <span>AI Marketer</span>
        </Link>
        <div className="admin-login-intro">
          <p className="admin-login-eyebrow">Operations workspace</p>
          <h1>Turn attention into momentum.</h1>
          <p>Manage your leads, campaigns, emails and content from one calm, focused workspace.</p>
        </div>
        <div className="admin-login-status"><span /> Systems ready for your next move</div>
      </section>

      <section className="admin-login-panel">
        <Link href="/" className="admin-login-back">← Back to AI Marketer</Link>
        <form onSubmit={handleSubmit} className="admin-login-form">
          <div className="admin-login-heading">
            <p className="admin-login-eyebrow">Admin access</p>
            <h2>Admin login</h2>
            <p>Welcome back. Sign in to continue to your workspace.</p>
          </div>
          <div className="admin-login-field">
            <label htmlFor="email">Email address</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          </div>
          <div className="admin-login-field">
            <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          </div>
          {error && <p className="admin-login-error" role="alert">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="admin-login-submit"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
        </form>
        <p className="admin-login-note">Protected workspace for authorised team members.</p>
      </section>
    </main>
  );
}
