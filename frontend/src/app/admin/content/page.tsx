"use client";

import { useEffect, useState } from "react";
import { apiFetchWithAuth } from "@/lib/api";
import type { Content } from "@/types";
import { useAuth } from "../_components/auth-context";

const statusStyles: Record<string, string> = {
  published: "bg-green-100 text-green-800",
  draft: "bg-gray-100 text-gray-800",
  scheduled: "bg-blue-100 text-blue-800",
};

export default function ContentPage() {
  const { token } = useAuth();
  const [content, setContent] = useState<Content[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formError, setFormError] = useState("");
  const [form, setForm] = useState({ type: "blog_post", title: "", status: "draft", date: "", excerpt: "", tag: "" });

  useEffect(() => {
    if (!token) return;
    apiFetchWithAuth<Content[]>("/content", token)
      .then(setContent)
      .catch(() => {});
  }, [token]);

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Content</h1>
        <button type="button" onClick={() => setShowForm((value) => !value)} className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white">{showForm ? "Close" : "Create content"}</button>
      </div>
      {showForm && (
        <form onSubmit={createContent} className="grid gap-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2">
          <label className="text-sm font-medium text-slate-700">Type<input required value={form.type} onChange={(event) => setForm({ ...form, type: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label>
          <label className="text-sm font-medium text-slate-700">Status<select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal"><option value="draft">Draft</option><option value="scheduled">Scheduled</option><option value="published">Published</option></select></label>
          <label className="text-sm font-medium text-slate-700 md:col-span-2">Title<input required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label>
          <label className="text-sm font-medium text-slate-700 md:col-span-2">Excerpt<textarea value={form.excerpt} onChange={(event) => setForm({ ...form, excerpt: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label>
          <label className="text-sm font-medium text-slate-700">Date<input value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label>
          <label className="text-sm font-medium text-slate-700">Tag<input value={form.tag} onChange={(event) => setForm({ ...form, tag: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label>
          {formError && <p role="alert" className="text-sm text-red-700 md:col-span-2">{formError}</p>}
          <button type="submit" className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white md:col-span-2">Save content</button>
        </form>
      )}

      {content.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center">
          <p className="text-slate-500">No content found. Create your first content to get started.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Title</th>
                <th className="px-4 py-3 text-left font-medium">Type</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-left font-medium">Date</th>
                <th className="px-4 py-3 text-left font-medium">Tag</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {content.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{item.title}</td>
                  <td className="px-4 py-3 text-slate-700">{item.type}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${statusStyles[item.status] || "bg-gray-100 text-gray-800"}`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{item.date}</td>
                  <td className="px-4 py-3 text-slate-700">{item.tag}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );

  async function createContent(event: React.FormEvent) {
    event.preventDefault();
    if (!token) return;
    setFormError("");
    try {
      const created = await apiFetchWithAuth<Content>("/content/", token, { method: "POST", body: JSON.stringify({ ...form, id: crypto.randomUUID(), image_url: "" }) });
      setContent((current) => [...current, created]);
      setForm({ type: "blog_post", title: "", status: "draft", date: "", excerpt: "", tag: "" });
      setShowForm(false);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Could not create content");
    }
  }
}
