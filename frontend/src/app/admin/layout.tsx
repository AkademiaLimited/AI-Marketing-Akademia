import type { Metadata } from "next";
import "./admin.css";
import { AuthProvider } from "./_components/auth-context";
import AdminLayoutClient from "./_components/AdminLayoutClient";

export const metadata: Metadata = {
  title: "Admin | AI Marketer",
};

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <AdminLayoutClient>{children}</AdminLayoutClient>
    </AuthProvider>
  );
}
