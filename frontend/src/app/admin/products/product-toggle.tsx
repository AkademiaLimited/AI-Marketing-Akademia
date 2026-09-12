"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { apiFetchWithAuth } from "@/lib/api";

export default function ProductToggle({
  product,
  token,
}: {
  product: { id: string; slug: string; published: boolean };
  token: string | null;
}) {
  const router = useRouter();
  const [error, setError] = useState("");

  async function toggle() {
    setError("");
    try {
      await apiFetchWithAuth(`/products/${product.slug}`, token, {
        method: "PATCH",
        body: JSON.stringify({ published: !product.published }),
      });
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update product");
    }
  }

  return (
    <div>
      <button
        onClick={toggle}
        className={`inline-flex rounded-full px-3 py-1 text-xs font-medium transition-colors ${
          product.published
            ? "bg-emerald-100 text-emerald-800 hover:bg-emerald-200"
            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
        }`}
      >
        {product.published ? "Published" : "Unpublished"}
      </button>
      {error && <p role="alert" className="mt-1 max-w-xs text-xs text-red-700">{error}</p>}
    </div>
  );
}
