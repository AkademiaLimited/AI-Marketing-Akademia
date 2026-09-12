"use client";

import { useEffect, useState } from "react";
import { apiFetchWithAuth } from "@/lib/api";
import type { Lead, LeadStatus } from "@/types";
import Link from "next/link";
import { useAuth } from "../_components/auth-context";

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

export default function LeadsPage() {
  const { token } = useAuth();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formError, setFormError] = useState("");
  const [form, setForm] = useState({ company: "", contact: "", email: "", website: "", industry: "", location: "", product_id: "", problem: "" });

  useEffect(() => {
    if (!token) return;
    apiFetchWithAuth<Lead[]>("/leads", token)
      .then(setLeads)
      .catch(() => {});
  }, [token]);

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Leads</h1>
        <button type="button" onClick={() => setShowForm((value) => !value)} className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white">{showForm ? "Close" : "Add lead"}</button>
      </div>
      {showForm && (
        <form onSubmit={createLead} className="grid gap-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2">
          {(["company", "contact", "email", "website", "industry", "location", "product_id"] as const).map((field) => (
            <label key={field} className="text-sm font-medium text-slate-700">{field.replace("_", " ")}
              <input required={field === "company" || field === "email" || field === "product_id"} type={field === "email" ? "email" : "text"} value={form[field]} onChange={(event) => setForm({ ...form, [field]: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" />
            </label>
          ))}
          <label className="text-sm font-medium text-slate-700 md:col-span-2">Problem
            <textarea value={form.problem} onChange={(event) => setForm({ ...form, problem: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" />
          </label>
          {formError && <p role="alert" className="text-sm text-red-700 md:col-span-2">{formError}</p>}
          <button type="submit" className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white md:col-span-2">Save lead</button>
        </form>
      )}

      {leads.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center">
          <p className="text-slate-500">No leads found. Add your first lead to get started.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Company</th>
                <th className="px-4 py-3 text-left font-medium">Contact</th>
                <th className="px-4 py-3 text-left font-medium">Email</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-left font-medium">Product</th>
                <th className="px-4 py-3 text-left font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{lead.company}</td>
                  <td className="px-4 py-3 text-slate-700">{lead.contact}</td>
                  <td className="px-4 py-3 text-slate-700">{lead.email}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${statusStyles[lead.status]}`}>
                      {statusLabels[lead.status]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{lead.product_id}</td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/admin/leads/${lead.id}`}
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );

  async function createLead(event: React.FormEvent) {
    event.preventDefault();
    if (!token) return;
    setFormError("");
    try {
      const created = await apiFetchWithAuth<Lead>("/leads/", token, { method: "POST", body: JSON.stringify({ ...form, id: crypto.randomUUID(), status: "new", reasoning: "", last_contact: "" }) });
      setLeads((current) => [...current, created]);
      setShowForm(false);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Could not create lead");
    }
  }
}
