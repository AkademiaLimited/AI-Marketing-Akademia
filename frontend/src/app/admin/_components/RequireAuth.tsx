"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "./auth-context";

export default function RequireAuth({ children }: { children: React.ReactNode }) {
  const { token, user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!token || !user?.is_superuser)) {
      router.replace("/admin/login");
    }
  }, [token, user, loading, router]);

  if (loading) {
    return <div className="p-6 text-sm text-slate-500">Loading...</div>;
  }
  if (!token || !user?.is_superuser) {
    return null;
  }
  return <>{children}</>;
}
