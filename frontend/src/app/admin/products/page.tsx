"use client";

import { useEffect, useState } from "react";
import { apiFetchWithAuth } from "@/lib/api";
import type { Product } from "@/types";
import ProductToggle from "./product-toggle";
import PublishButton from "./publish-button";
import { useAuth } from "../_components/auth-context";

export default function AdminProductsPage() {
  const { token } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formError, setFormError] = useState("");
  const [form, setForm] = useState({ name: "", slug: "", problem: "", target: "", description: "", category: "general", price: "" });

  useEffect(() => {
    if (!token) return;
    apiFetchWithAuth<Product[]>("/products", token)
      .then(setProducts)
      .catch(() => {});
  }, [token]);

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Products</h1>
        <button type="button" onClick={() => setShowForm((value) => !value)} className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white">
          {showForm ? "Close" : "Create product"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={createProduct} className="grid gap-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2">
          {(["name", "slug", "category", "price", "target"] as const).map((field) => (
            <label key={field} className="text-sm font-medium text-slate-700">{field}
              <input required={field !== "price"} value={form[field]} onChange={(event) => setForm({ ...form, [field]: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" />
            </label>
          ))}
          <label className="text-sm font-medium text-slate-700 md:col-span-2">Problem
            <textarea required value={form.problem} onChange={(event) => setForm({ ...form, problem: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" />
          </label>
          <label className="text-sm font-medium text-slate-700 md:col-span-2">Description
            <textarea required value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" />
          </label>
          {formError && <p role="alert" className="text-sm text-red-700 md:col-span-2">{formError}</p>}
          <button type="submit" className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white md:col-span-2">Save product</button>
        </form>
      )}

      {products.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center">
          <p className="text-slate-500">No products found. Add your first product to get started.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Name</th>
                <th className="px-4 py-3 text-left font-medium">Slug</th>
                <th className="px-4 py-3 text-left font-medium">Published</th>
                <th className="px-4 py-3 text-left font-medium">Marketing</th>
                <th className="px-4 py-3 text-left font-medium">Description</th>
                <th className="px-4 py-3 text-left font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {products.map((product) => (
                <tr key={product.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{product.name}</td>
                  <td className="px-4 py-3 text-slate-700 font-mono text-xs">{product.slug}</td>
                  <td className="px-4 py-3">
                    <ProductToggle product={product} token={token} />
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                      product.marketing_status === "completed"
                        ? "bg-green-100 text-green-800"
                        : product.marketing_status === "queued" || product.marketing_status === "running"
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-gray-100 text-gray-800"
                    }`}>
                      {product.marketing_status || "pending"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-700 max-w-xs truncate">
                    {product.description}
                  </td>
                  <td className="px-4 py-3">
                    <PublishButton product={product} token={token} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );

  async function createProduct(event: React.FormEvent) {
    event.preventDefault();
    if (!token) return;
    setFormError("");
    try {
      const created = await apiFetchWithAuth<Product>("/products/", token, { method: "POST", body: JSON.stringify({ ...form, id: crypto.randomUUID(), features: [], benefits: [], capabilities: [] }) });
      setProducts((current) => [...current, created]);
      setForm({ name: "", slug: "", problem: "", target: "", description: "", category: "general", price: "" });
      setShowForm(false);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Could not create product");
    }
  }
}
