"use client";

import { usePathname } from "next/navigation";
import AdminSidebar from "./Sidebar";
import RequireAuth from "./RequireAuth";

export default function AdminLayoutClient({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname === "/admin/login") {
    return <>{children}</>;
  }

  return (
    <div className="admin-body">
      <AdminSidebar />
      <div className="main">
        <div className="topbar">
          <div className="crumb">
            <b>Admin</b>
          </div>
          <div className="topbar-right">
            <div className="avatar">AM</div>
          </div>
        </div>
        <RequireAuth>
          <div id="workspace">{children}</div>
        </RequireAuth>
      </div>
    </div>
  );
}