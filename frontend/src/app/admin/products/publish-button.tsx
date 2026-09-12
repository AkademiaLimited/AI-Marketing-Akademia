"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetchWithAuth } from "@/lib/api";

export default function PublishButton({
  product,
  token,
}: {
  product: { slug: string; marketing_status: string; id: string };
  token: string | null;
}) {
  const [status, setStatus] = useState<"idle" | "publishing" | "published" | "error">("idle");
  const router = useRouter();

  const handlePublish = async () => {
    setStatus("publishing");
    try {
      await apiFetchWithAuth(`/products/${product.slug}/publish`, token, {
        method: "POST",
      });
      setStatus("published");
      router.refresh();
    } catch {
      setStatus("error");
    }
  };

  if (product.marketing_status === "completed") {
    return (
      <span className="inline-flex rounded-full px-2 py-1 text-xs font-medium bg-green-100 text-green-800">
        Marketing complete
      </span>
    );
  }

  if (product.marketing_status === "queued" || product.marketing_status === "running") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800">
        <span className="animate-spin h-2 w-2 border border-current border-t-transparent rounded-full"></span>
        Running...
      </span>
    );
  }

  if (status === "error") {
    return (
      <div>
        <button onClick={handlePublish} className="rounded-md bg-slate-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-slate-800">
          Retry publishing
        </button>
        <p role="alert" className="mt-1 text-xs text-red-700">Publishing failed. Check the backend logs.</p>
      </div>
    );
  }

  return (
    <button
      onClick={handlePublish}
      disabled={status === "publishing"}
      className="rounded-md bg-slate-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-slate-800 disabled:opacity-50"
    >
      {status === "publishing" ? "Publishing..." : "Publish to Marketing"}
    </button>
  );
}
