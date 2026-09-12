"use client";

import { useEffect, useState } from "react";
import { apiFetchWithAuth } from "@/lib/api";
import type { Automation, MarketingActivity } from "@/types";
import { useAuth } from "../_components/auth-context";

const statusStyles: Record<string, string> = {
  running: "bg-green-100 text-green-800",
  paused: "bg-yellow-100 text-yellow-800",
  completed: "bg-slate-100 text-slate-800",
  failed: "bg-red-100 text-red-800",
  stopped: "bg-gray-100 text-gray-800",
};

export default function AutomationPage() {
  const { token } = useAuth();
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [activities, setActivities] = useState<MarketingActivity[]>([]);

  useEffect(() => {
    if (!token) return;
    apiFetchWithAuth<Automation[]>("/automations", token)
      .then(setAutomations)
      .catch(() => {});
    apiFetchWithAuth<MarketingActivity[]>("/workflows/activities", token)
      .then(setActivities)
      .catch(() => {});
  }, [token]);

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Automation</h1>

      {automations.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center">
          <p className="text-slate-500">No automations found. Create your first automation to get started.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Name</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-left font-medium">Last run</th>
                <th className="px-4 py-3 text-left font-medium">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {automations.map((automation) => (
                <tr key={automation.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{automation.name}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${statusStyles[automation.status] || "bg-gray-100 text-gray-800"}`}>
                      {automation.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{automation.last_run}</td>
                  <td className="px-4 py-3 text-slate-700">{automation.result}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">Recent activity</h2>
          <p className="mt-1 text-sm text-slate-500">A record of research, AI decisions, drafts, and failures.</p>
        </div>
        {activities.length === 0 ? (
          <p className="p-6 text-sm text-slate-500">No workflow activity recorded yet.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {activities.map((activity) => (
              <div key={activity.id} className="grid gap-2 px-6 py-4 md:grid-cols-[180px_1fr_auto] md:items-start">
                <div className="text-xs text-slate-500">{activity.created_at}</div>
                <div>
                  <div className="font-medium text-slate-900">{activity.activity_type.replaceAll("_", " ")}</div>
                  <div className="text-sm text-slate-600">{activity.details || "No details recorded."}</div>
                  {activity.source_url && <div className="mt-1 truncate text-xs text-slate-400">Source: {activity.source_url}</div>}
                  {activity.error && <div className="mt-1 text-sm text-red-700">Cause: {activity.error}</div>}
                </div>
                <span className={`inline-flex w-fit rounded-full px-2 py-1 text-xs font-medium ${activity.status === "failed" ? "bg-red-100 text-red-800" : "bg-slate-100 text-slate-700"}`}>
                  {activity.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
