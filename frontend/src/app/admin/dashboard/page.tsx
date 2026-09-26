"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { apiFetchWithAuth } from "@/lib/api";
import type { Lead } from "@/types";
import { useAuth } from "../_components/auth-context";

type DashboardSummary = {
  new: number;
  contacted: number;
  responded: number;
  needs_followup: number;
  meetings: number;
  customers: number;
  lost: number;
};

type DashboardProgress = {
  marketing_pipeline: Record<string, number>;
  lead_funnel: Record<string, number>;
  email_pipeline: Record<string, number>;
  campaign_status: Record<string, number>;
  workflow_runs: Record<string, number>;
  active_brand: string | null;
  recent_activity: Array<{
    id: string;
    activity_type: string;
    status: string;
    details: string;
    created_at: string;
  }>;
};

type PendingProduct = {
  id: string;
  slug: string;
  name: string;
  marketing_status: string;
};

const LEAD_STATUSES = [
  { key: "new", label: "New Leads" },
  { key: "contacted", label: "Contacted" },
  { key: "responded", label: "Responded" },
  { key: "meeting", label: "Meetings" },
  { key: "customer", label: "Customers" },
  { key: "lost", label: "Lost" },
];

const MARKETING_STATUSES = [
  { key: "pending", label: "Pending", color: "bg-gray-200" },
  { key: "queued", label: "Queued", color: "bg-yellow-200" },
  { key: "running", label: "Running", color: "bg-blue-200" },
  { key: "completed", label: "Completed", color: "bg-green-200" },
  { key: "failed", label: "Failed", color: "bg-red-200" },
];

const CAMPAIGN_STATUSES = [
  { key: "running", label: "Running" },
  { key: "paused", label: "Paused" },
  { key: "completed", label: "Completed" },
  { key: "stopped", label: "Stopped" },
];

const ACTIVITY_STATUS_COLORS: Record<string, string> = {
  completed: "bg-slate-100 text-slate-700",
  failed: "bg-red-100 text-red-800",
  qualified: "bg-green-100 text-green-800",
  running: "bg-blue-100 text-blue-800",
};

function BarChart({
  data,
  labels,
  colors,
}: {
  data: Record<string, number>;
  labels: { key: string; label: string }[];
  colors?: Record<string, string>;
}) {
  const maxValue = Math.max(...labels.map((l) => data[l.key] || 0), 1);
  return (
    <div className="space-y-2">
      {labels.map((item) => {
        const value = data[item.key] || 0;
        const barWidth = (value / maxValue) * 100;
        const barColor = colors ? colors[item.key] : "bg-slate-700";
        return (
          <div key={item.key} className="flex items-center gap-3 text-sm">
            <span className="w-24 text-xs text-slate-600">{item.label}</span>
            <div className="relative h-6 flex-1 overflow-hidden rounded-md bg-slate-100">
              <div
                className={`h-full rounded-md transition-all duration-500 ${barColor}`}
                style={{ width: `${barWidth}%` }}
              />
              <span className="absolute inset-0 flex items-center justify-end px-2 text-xs font-medium text-slate-800">
                {value}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ProgressBar({
  steps,
  data,
}: {
  steps: { key: string; label: string; color: string }[];
  data: Record<string, number>;
}) {
  const total = steps.reduce((sum, s) => sum + (data[s.key] || 0), 0);
  if (total === 0) return <p className="text-sm text-slate-500">No marketing activity yet.</p>;

  const { segments } = steps.reduce(
    (acc, s) => {
      const value = data[s.key] || 0;
      if (value === 0) return acc;
      const width = (value / total) * 100;
      acc.segments.push({ ...s, width, left: acc.cumulative });
      acc.cumulative += width;
      return acc;
    },
    { segments: [] as Array<{ key: string; label: string; color: string; width: number; left: number }>, cumulative: 0 },
  );

  return (
    <div className="space-y-2">
      <div className="relative h-6 w-full overflow-hidden rounded-md border border-slate-200">
        {segments.map((step) => (
          <div
            key={step.key}
            className={`absolute top-0 h-full ${step.color}`}
            style={{ left: `${step.left}%`, width: `${step.width}%` }}
            title={`${step.label}: ${data[step.key] || 0}`}
          />
        ))}
      </div>
      <div className="grid grid-cols-3 gap-2 text-xs text-slate-600">
        {segments.map((s) => (
          <div key={s.key} className="flex items-center gap-1">
            <span className={`h-2 w-2 rounded ${s.color}`} />
            <span>{s.label}</span>
            <span className="font-medium">{data[s.key] || 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { token } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary>({
    new: 0, contacted: 0, responded: 0, needs_followup: 0,
    meetings: 0, customers: 0, lost: 0,
  });
  const [progress, setProgress] = useState<DashboardProgress>({
    marketing_pipeline: {},
    lead_funnel: {},
    email_pipeline: {},
    campaign_status: {},
    workflow_runs: {},
    active_brand: null,
    recent_activity: [],
  });
  const [leads, setLeads] = useState<Lead[]>([]);
  const [campaigns, setCampaigns] = useState<{ status: string }[]>([]);
  const [products, setProducts] = useState<PendingProduct[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  const doFetch = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        apiFetchWithAuth<DashboardSummary>("/dashboard/summary", token),
        apiFetchWithAuth<DashboardProgress>("/dashboard/progress", token),
        apiFetchWithAuth<Lead[]>("/leads", token),
        apiFetchWithAuth<{ status: string }[]>("/campaigns", token),
        apiFetchWithAuth<PendingProduct[]>("/products", token),
      ]);
      if (results[0].status === "fulfilled") setSummary(results[0].value);
      if (results[1].status === "fulfilled") setProgress(results[1].value);
      if (results[2].status === "fulfilled") setLeads(results[2].value);
      if (results[3].status === "fulfilled") setCampaigns(results[3].value);
      if (results[4].status === "fulfilled") setProducts(results[4].value);
      setLastUpdated(new Date());
    } catch {
      // Silent fail — keep showing last data
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    const timer = setTimeout(() => void doFetch(), 0);
    return () => clearTimeout(timer);
  }, [doFetch]);

  useEffect(() => {
    if (!token) return;
    const timer = setInterval(() => void doFetch(), 15000);
    return () => clearInterval(timer);
  }, [doFetch, token]);

  const router = useRouter();

  const needsAttention = leads.filter(
    (l) => l.status === "needs-followup" || l.status === "new"
  );

  const runningAutomations = campaigns.filter((c) => c.status === "running").length;
  const pausedAutomations = campaigns.filter((c) => c.status === "paused").length;
  const completedAutomations = campaigns.filter((c) => c.status === "completed").length;

  const totalLeads = Object.values(progress.lead_funnel).reduce((a, b) => a + b, 0);

  const pendingProducts = products.filter(
    (p) => p.marketing_status === "pending" || !p.marketing_status
  );

  const handleRunMarketing = async (product: PendingProduct) => {
    if (!token) return;
    setActionLoading((m) => ({ ...m, [product.id]: true }));
    try {
      await apiFetchWithAuth(`/products/${product.slug}/publish`, token, { method: "POST" });
      setProducts((current) =>
        current.map((p) =>
          p.id === product.id ? { ...p, marketing_status: "queued" } : p,
        ),
      );
    } catch {
      // Error handled by UI refresh on next poll
    } finally {
      setActionLoading((m) => {
        const copy = { ...m };
        delete copy[product.id];
        return copy;
      });
    }
  };

  return (
    <div className="view">
      <div className="view-header">
        <div>
          <h1>Dashboard</h1>
          <p>Marketing overview</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-500">
          {loading && <span data-testid="loading">Refreshing...</span>}
          {lastUpdated && (
            <span data-testid="last-updated">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {progress.active_brand && (
        <div className="mb-4 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm">
          <span className="font-medium text-slate-700">Active brand:</span>
          {" "}
          <span className="text-slate-900">{progress.active_brand}</span>
          <span
            className="ml-2 inline-block h-3 w-3 rounded"
            style={{ backgroundColor: progress.active_brand ? "#1F6F5C" : undefined }}
          />
          <button
            onClick={() => router.push("/admin/brands")}
            className="ml-2 text-xs text-slate-500 underline hover:text-slate-700"
          >
            Manage brand
          </button>
        </div>
      )}

      <div className="mb-4 flex flex-wrap gap-2">
        <button
          onClick={() => router.push("/admin/brands")}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          data-testid="manage-brands-btn"
        >
          Manage brands
        </button>
        <button
          onClick={() => router.push("/admin/products")}
          className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800"
          data-testid="view-products-btn"
        >
          View products
        </button>
        <button
          onClick={() => router.push("/admin/leads")}
          className="rounded-md bg-blue-700 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800"
          data-testid="view-leads-btn"
        >
          View leads
        </button>
        {pendingProducts.length > 0 && (
          <button
            onClick={() => router.push("/admin/products")}
            className="rounded-md bg-amber-700 px-4 py-2 text-sm font-medium text-white hover:bg-amber-800"
            data-testid="generate-content-btn"
          >
            Generate content ({pendingProducts.length})
          </button>
        )}
      </div>

      <div className="stat-row">
        <div className="card stat-card">
          <div className="label">New</div>
          <div className="num">{summary.new}</div>
        </div>
        <div className="card stat-card">
          <div className="label">Contacted</div>
          <div className="num">{summary.contacted}</div>
        </div>
        <div className="card stat-card">
          <div className="label">Responded</div>
          <div className="num">{summary.responded}</div>
        </div>
        <div className="card stat-card">
          <div className="label">Meetings</div>
          <div className="num">{summary.meetings}</div>
        </div>
        <div className="card stat-card">
          <div className="label">Customers</div>
          <div className="num">{summary.customers}</div>
        </div>
      </div>

      <div className="dash-grid">
        <div className="card pad">
          <h2 className="mb-3 text-sm font-medium text-slate-700">Marketing Pipeline</h2>
          <ProgressBar steps={MARKETING_STATUSES} data={progress.marketing_pipeline} />
          <div className="mt-3 text-xs text-slate-500">
            Total products tracked: {Object.values(progress.marketing_pipeline).reduce((a, b) => a + b, 0)}
          </div>
        </div>

        <div className="card pad">
          <h2 className="mb-3 text-sm font-medium text-slate-700">Lead Funnel</h2>
          <BarChart data={progress.lead_funnel} labels={LEAD_STATUSES} />
          <div className="mt-3 text-xs text-slate-500">
            Total leads: {totalLeads}
          </div>
        </div>

        <div className="card pad">
          <h2 className="mb-3 text-sm font-medium text-slate-700">Email Pipeline</h2>
          {Object.keys(progress.email_pipeline).length === 0 ? (
            <p className="text-sm text-slate-500">No emails yet.</p>
          ) : (
            <BarChart
              data={progress.email_pipeline}
              labels={[
                { key: "draft", label: "Drafts" },
                { key: "sent", label: "Sent" },
                { key: "review", label: "Review" },
              ]}
            />
          )}
        </div>

        <div className="card pad">
          <h2 className="mb-3 text-sm font-medium text-slate-700">Campaign Status</h2>
          {Object.keys(progress.campaign_status).length === 0 ? (
            <p className="text-sm text-slate-500">No campaigns running.</p>
          ) : (
            <BarChart data={progress.campaign_status} labels={CAMPAIGN_STATUSES} />
          )}
          <div className="mt-3 flex gap-4 text-xs">
            <span className="text-blue-700">Running: {runningAutomations}</span>
            <span className="text-yellow-700">Paused: {pausedAutomations}</span>
            <span className="text-green-700">Completed: {completedAutomations}</span>
          </div>
        </div>
       </div>

      {pendingProducts.length > 0 && (
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-3 text-sm font-medium text-slate-700">Products ready for marketing</h2>
          <p className="mb-3 text-xs text-slate-500">
            These products have not yet been published to the marketing pipeline. Click to trigger.
          </p>
          <div className="space-y-2">
            {pendingProducts.map((product) => (
              <div key={product.id} className="flex items-center justify-between rounded-md border border-slate-100 px-4 py-2">
                <div>
                  <span className="font-medium text-slate-900">{product.name}</span>
                  <span className="text-xs text-slate-500"> /{product.slug}</span>
                </div>
                <button
                  onClick={() => void handleRunMarketing(product)}
                  disabled={actionLoading[product.id]}
                  className="rounded-md bg-slate-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-slate-800 disabled:opacity-50"
                  data-testid={`publish-${product.id}`}
                >
                  {actionLoading[product.id] ? "Publishing..." : "Run marketing"}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card pipeline">
        <div className="label">Lead Pipeline</div>
        <div className="num">{summary.new}</div>
        <div className="pl-line"></div>
        <div className="label">Contacted</div>
        <div className="num">{summary.contacted}</div>
        <div className="pl-line"></div>
        <div className="label">Responded</div>
        <div className="num">{summary.responded}</div>
        <div className="pl-line"></div>
        <div className="label">Meetings</div>
        <div className="num">{summary.meetings}</div>
        <div className="pl-line"></div>
        <div className="label">Customers</div>
        <div className="num">{summary.customers}</div>
      </div>

      <div className="dash-grid">
        <div className="card pad">
          <div className="section-title">Needs your attention</div>
          {needsAttention.length > 0 ? (
            needsAttention.slice(0, 5).map((l) => (
              <div className="attn-row" key={l.id}>
                <div className="attn-dot"></div>
                <div>
                  <div className="co">{l.company}</div>
                  <div className="why">{l.status === "needs-followup" ? "Needs follow-up" : "New lead"}</div>
                </div>
              </div>
            ))
          ) : (
            <div className="empty">Nothing needs attention right now.</div>
          )}
        </div>

        <div className="card pad">
          <div className="section-title">Recent activity</div>
          <p className="mt-1 text-sm text-slate-500">Latest system events and AI decisions.</p>
          {progress.recent_activity.length === 0 ? (
            <p className="mt-2 text-sm text-slate-500">No activity recorded yet.</p>
          ) : (
            <div className="mt-2 space-y-2">
              {progress.recent_activity.map((activity) => (
                <div key={activity.id} className="border-l-2 border-slate-200 pl-3 py-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-700">
                      {activity.activity_type.replace("_", " ")}
                    </span>
                    <span
                      className={`rounded-full px-1.5 py-0.5 text-xs font-medium ${
                        ACTIVITY_STATUS_COLORS[activity.status] || "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {activity.status}
                    </span>
                  </div>
                  {activity.details && (
                    <span className="text-slate-500">{activity.details}</span>
                  )}
                  <div className="text-slate-400">{activity.created_at}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
