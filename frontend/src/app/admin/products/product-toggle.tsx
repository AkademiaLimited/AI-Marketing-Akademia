"use client";

import { useRouter } from "next/navigation";
import { apiFetchWithAuth } from "@/lib/api";

export default function ProductToggle({
  product,
  token,
}: {
  product: { id: string; slug: string; published: boolean };
  token: string | null;
}) {
  const router = useRouter();

  async function toggle() {
    try {
      await apiFetchWithAuth(`/products/${product.slug}`, token, {
        method: "PATCH",
        body: JSON.stringify({ published: !product.published }),
      });
      router.refresh();
    } catch (err) {
      console.error(err);
      alert("Failed to update product. Ensure the backend PATCH endpoint is available.");
    }
  }

  return (
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
  );
}
