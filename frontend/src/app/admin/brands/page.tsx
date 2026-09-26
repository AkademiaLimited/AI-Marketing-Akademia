"use client";

import { useEffect, useState } from "react";
import { apiFetchWithAuth } from "@/lib/api";
import type { BrandProfile } from "@/types";
import { useAuth } from "../_components/auth-context";

const DEFAULT_FORM = {
  name: "",
  voice_description: "",
  primary_color: "#1F6F5C",
  secondary_color: "#3AAFA9",
  font_family: "Inter, sans-serif",
  tone_keywords: "",
};

export default function BrandsPage() {
  const { token, user } = useAuth();
  const [brands, setBrands] = useState<BrandProfile[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formError, setFormError] = useState("");
  const [form, setForm] = useState(DEFAULT_FORM);

  useEffect(() => {
    if (!token) return;
    apiFetchWithAuth<BrandProfile[]>("/brands", token)
      .then(setBrands)
      .catch(() => {});
  }, [token]);

  const resetForm = () => {
    setForm(DEFAULT_FORM);
    setEditingId(null);
    setShowForm(false);
    setFormError("");
  };

  const handleEdit = (brand: BrandProfile) => {
    setForm({
      name: brand.name,
      voice_description: brand.voice_description,
      primary_color: brand.primary_color,
      secondary_color: brand.secondary_color,
      font_family: brand.font_family,
      tone_keywords: brand.tone_keywords,
    });
    setEditingId(brand.id);
    setShowForm(true);
    setFormError("");
  };

  const handleDelete = async (id: string) => {
    if (!token) return;
    try {
      await apiFetchWithAuth(`/brands/${id}`, token, { method: "DELETE" });
      setBrands((current) => current.filter((b) => b.id !== id));
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Could not delete brand");
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!token || !user) return;
    setFormError("");
    try {
      if (editingId) {
        const updated = await apiFetchWithAuth<BrandProfile>(
          `/brands/${editingId}`,
          token,
          { method: "PATCH", body: JSON.stringify(form) },
        );
        setBrands((current) =>
          current.map((b) => (b.id === editingId ? updated : b)),
        );
      } else {
        const created = await apiFetchWithAuth<BrandProfile>(
          `/brands/?user_id=${user.id}`,
          token,
          { method: "POST", body: JSON.stringify(form) },
        );
        setBrands((current) => [...current, created]);
      }
      resetForm();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Could not save brand");
    }
  };

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Brand Profiles</h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage your brand identity so AI-generated content stays on-brand.
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            resetForm();
            setShowForm(true);
          }}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white"
        >
          {showForm && editingId ? "Close" : "New brand profile"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="grid gap-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2">
          <label className="text-sm font-medium text-slate-700">Name
            <input
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal"
              placeholder="e.g. Acmeco"
            />
          </label>

          <label className="text-sm font-medium text-slate-700">Tone keywords
            <input
              value={form.tone_keywords}
              onChange={(e) => setForm({ ...form, tone_keywords: e.target.value })}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal"
              placeholder="professional,approachable,innovative"
            />
          </label>

          <label className="text-sm font-medium text-slate-700">Primary color
            <div className="mt-1 flex items-center gap-2">
              <input
                type="color"
                value={form.primary_color}
                onChange={(e) => setForm({ ...form, primary_color: e.target.value })}
                className="h-8 w-12 cursor-pointer rounded border border-slate-300 p-0"
              />
              <input
                required
                value={form.primary_color}
                onChange={(e) => setForm({ ...form, primary_color: e.target.value })}
                className="flex-1 rounded-md border border-slate-300 px-3 py-2 font-normal font-mono text-xs"
              />
            </div>
          </label>

          <label className="text-sm font-medium text-slate-700">Secondary color
            <div className="mt-1 flex items-center gap-2">
              <input
                type="color"
                value={form.secondary_color}
                onChange={(e) => setForm({ ...form, secondary_color: e.target.value })}
                className="h-8 w-12 cursor-pointer rounded border border-slate-300 p-0"
              />
              <input
                required
                value={form.secondary_color}
                onChange={(e) => setForm({ ...form, secondary_color: e.target.value })}
                className="flex-1 rounded-md border border-slate-300 px-3 py-2 font-normal font-mono text-xs"
              />
            </div>
          </label>

          <label className="text-sm font-medium text-slate-700 md:col-span-2">Font family
            <input
              value={form.font_family}
              onChange={(e) => setForm({ ...form, font_family: e.target.value })}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal"
              placeholder="e.g. Inter, sans-serif"
            />
          </label>

          <label className="text-sm font-medium text-slate-700 md:col-span-2">Brand voice description
            <textarea
              value={form.voice_description}
              onChange={(e) => setForm({ ...form, voice_description: e.target.value })}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal"
              rows={3}
              placeholder="Describe your brand's tone and personality..."
            />
          </label>

          {formError && <p role="alert" className="text-sm text-red-700 md:col-span-2">{formError}</p>}
          <button type="submit" className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white md:col-span-2">
            {editingId ? "Update brand" : "Create brand"}
          </button>
        </form>
      )}

      {brands.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center">
          <p className="text-slate-500">No brand profiles found. Create one to start.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Name</th>
                <th className="px-4 py-3 text-left font-medium">Colors</th>
                <th className="px-4 py-3 text-left font-medium">Font</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {brands.map((brand) => (
                <tr key={brand.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{brand.name}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span
                        className="h-4 w-4 rounded"
                        style={{ backgroundColor: brand.primary_color }}
                        title={brand.primary_color}
                      />
                      <span
                        className="h-4 w-4 rounded"
                        style={{ backgroundColor: brand.secondary_color }}
                        title={brand.secondary_color}
                      />
                      <span className="text-xs text-slate-500">{brand.primary_color}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{brand.font_family}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${brand.is_active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}>
                      {brand.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right space-x-1">
                    <button
                      onClick={() => handleEdit(brand)}
                      className="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-200"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(brand.id)}
                      className="rounded-md bg-red-100 px-2.5 py-1 text-xs font-medium text-red-700 hover:bg-red-200"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
