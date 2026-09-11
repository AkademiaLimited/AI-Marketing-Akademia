"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiFetchWithAuth } from "@/lib/api";
import type { Lead, LeadStatus } from "@/types";
import LeadStatusForm from "./lead-status-form";
import { useAuth } from "../../_components/auth-context";

const statusStyles: Record<LeadStatus, string> = {
  new: "bg-blue-100 text-blue-800",
  contacted: "bg-yellow-100 text-yellow-800",
  responded: "bg-green-100 text-green-800",
  "needs-followup": "bg-orange-100 text-orange-800",
  meeting: "bg-purple-100 text-purple-800",
  customer: "bg-emerald-100 text-emerald-800",
  lost: "bg-red-100 text-red-800",
};

const statusLabels: Record<LeadStatus, string> = {
  new: "New",
  contacted: "Contacted",
  responded: "Responded",
  "needs-followup": "Needs Follow-up",
  meeting: "Meeting",
  customer: "Customer",
  lost: "Lost",
};

export default function LeadDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const { token } = useAuth();
  const [lead, setLead] = useState<Lead | null>(null);

  useEffect(() => {
    if (!token) return;
    apiFetchWithAuth<Lead>(`/leads/${id}`, token)
      .then(setLead)
      .catch(() => {});
  }, [token, id]);

  if (!lead) {
    return (
      <section className="space-y-4">
        <h1 className="text-2xl font-semibold text-slate-900">Lead Not Found</h1>
        <p className="text-slate-600">The requested lead could not be found.</p>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">{lead.company}</h1>
        <span className={`inline-flex rounded-full px-3 py-1 text-sm font-medium ${statusStyles[lead.status]}`}>
          {statusLabels[lead.status]}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Contact Info</h2>
          <div className="grid grid-cols-1 gap-3 text-sm">
            <div>
              <div className="text-slate-500">Contact</div>
              <div className="font-medium text-slate-900">{lead.contact}</div>
            </div>
            <div>
              <div className="text-slate-500">Email</div>
              <div className="font-medium text-slate-900">{lead.email}</div>
            </div>
            <div>
              <div className="text-slate-500">Website</div>
              <div className="font-medium text-slate-900">{lead.website}</div>
            </div>
            <div>
              <div className="text-slate-500">Industry</div>
              <div className="font-medium text-slate-900">{lead.industry}</div>
            </div>
            <div>
              <div className="text-slate-500">Location</div>
              <div className="font-medium text-slate-900">{lead.location}</div>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Product & Status</h2>
          <div className="grid grid-cols-1 gap-3 text-sm">
            <div>
              <div className="text-slate-500">Product</div>
              <div className="font-medium text-slate-900">{lead.product_id}</div>
            </div>
            <div>
              <div className="text-slate-500">Last Contact</div>
              <div className="font-medium text-slate-900">{lead.last_contact || "—"}</div>
            </div>
          </div>
          <LeadStatusForm leadId={lead.id} currentStatus={lead.status} token={token} />
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Problem</h2>
        <p className="text-sm text-slate-700 whitespace-pre-wrap">{lead.problem}</p>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Discovery Notes & Reasoning</h2>
        <p className="text-sm text-slate-700 whitespace-pre-wrap">{lead.reasoning}</p>
      </div>
    </section>
  );
}
