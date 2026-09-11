"use client";

import { useRouter } from "next/navigation";
import type { LeadStatus } from "@/types";
import { apiFetchWithAuth } from "@/lib/api";

const statusOptions: LeadStatus[] = [
  "new",
  "contacted",
  "responded",
  "needs-followup",
  "meeting",
  "customer",
  "lost",
];

const statusLabels: Record<LeadStatus, string> = {
  new: "New",
  contacted: "Contacted",
  responded: "Responded",
  "needs-followup": "Needs Follow-up",
  meeting: "Meeting",
  customer: "Customer",
  lost: "Lost",
};

export default function LeadStatusForm({
  leadId,
  currentStatus,
  token,
}: {
  leadId: string;
  currentStatus: LeadStatus;
  token: string | null;
}) {
  const router = useRouter();

  async function handleChange(formData: FormData) {
    const newStatus = formData.get("status") as LeadStatus;
    try {
      await apiFetchWithAuth(`/leads/${leadId}/status`, token, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });
      router.refresh();
    } catch (err) {
      console.error(err);
      alert("Failed to update status");
    }
  }

  return (
    <form action={handleChange} className="flex items-center gap-3">
      <label className="text-sm text-slate-500">Update Status</label>
      <select
        name="status"
        defaultValue={currentStatus}
        className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none"
      >
        {statusOptions.map((s) => (
          <option key={s} value={s}>
            {statusLabels[s]}
          </option>
        ))}
      </select>
      <button
        type="submit"
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        Save
      </button>
    </form>
  );
}
