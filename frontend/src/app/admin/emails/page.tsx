"use client";

import { useEffect, useState } from "react";
import { apiFetchWithAuth } from "@/lib/api";
import type { Email } from "@/types";
import { useAuth } from "../_components/auth-context";

const statusStyles: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800",
  pending: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  sent: "bg-blue-100 text-blue-800",
  failed: "bg-red-100 text-red-800",
  responded: "bg-emerald-100 text-emerald-800",
};

export default function EmailsPage() {
  const { token } = useAuth();
  const [emails, setEmails] = useState<Email[]>([]);
  const [reviewingId, setReviewingId] = useState<string | null>(null);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ lead_name: "", product_name: "", subject: "", body: "" });

  useEffect(() => {
    if (!token) return;
    apiFetchWithAuth<Email[]>("/emails", token)
      .then(setEmails)
      .catch(() => {});
  }, [token]);

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Emails</h1>
        <button type="button" onClick={() => setShowForm((value) => !value)} className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white">{showForm ? "Close" : "Create draft"}</button>
      </div>
      {reviewError && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{reviewError}</p>}
      {showForm && (
        <form onSubmit={createDraft} className="grid gap-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          {(["lead_name", "product_name", "subject"] as const).map((field) => <label key={field} className="text-sm font-medium text-slate-700">{field.replace("_", " ")}<input required value={form[field]} onChange={(event) => setForm({ ...form, [field]: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label>)}
          <label className="text-sm font-medium text-slate-700">Body<textarea required value={form.body} onChange={(event) => setForm({ ...form, body: event.target.value })} className="mt-1 min-h-32 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label>
          <button type="submit" className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white">Save draft</button>
        </form>
      )}

      {emails.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center">
          <p className="text-slate-500">No emails found. Create your first email to get started.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Lead</th>
                <th className="px-4 py-3 text-left font-medium">Subject</th>
                <th className="px-4 py-3 text-left font-medium">Product</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-left font-medium">Review</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {emails.map((email) => (
                <tr key={email.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{email.lead_name}</td>
                  <td className="px-4 py-3 text-slate-700">{email.subject}</td>
                  <td className="px-4 py-3 text-slate-700">{email.product_name}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${statusStyles[email.status] || "bg-gray-100 text-gray-800"}`}>
                      {email.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {email.status === "draft" ? (
                      <div className="flex gap-2">
                        <button
                          type="button"
                          disabled={reviewingId === email.id}
                          className="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
                          onClick={() => reviewEmail(email.id, "approve")}
                        >
                          Approve
                        </button>
                        <button
                          type="button"
                          disabled={reviewingId === email.id}
                          className="rounded-md bg-red-100 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-200 disabled:opacity-50"
                          onClick={() => reviewEmail(email.id, "reject")}
                        >
                          Reject
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-400">Reviewed</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );

  async function reviewEmail(emailId: string, decision: "approve" | "reject") {
    if (!token) return;
    setReviewingId(emailId);
    setReviewError(null);
    try {
      const updated = await apiFetchWithAuth<Email>(`/emails/${emailId}/${decision}`, token, { method: "POST" });
      setEmails((current) => current.map((email) => email.id === updated.id ? updated : email));
    } catch (error) {
      setReviewError(error instanceof Error ? error.message : "Could not review email");
    } finally {
      setReviewingId(null);
    }
  }

  async function createDraft(event: React.FormEvent) {
    event.preventDefault();
    if (!token) return;
    setReviewError(null);
    try {
      const created = await apiFetchWithAuth<Email>("/emails/", token, { method: "POST", body: JSON.stringify({ ...form, id: crypto.randomUUID(), status: "draft" }) });
      setEmails((current) => [...current, created]);
      setForm({ lead_name: "", product_name: "", subject: "", body: "" });
      setShowForm(false);
    } catch (error) {
      setReviewError(error instanceof Error ? error.message : "Could not create email draft");
    }
  }
}
