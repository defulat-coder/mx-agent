"use client";

import { ExternalLink, ShieldAlert } from "lucide-react";
import { useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import { cn } from "@/lib/utils";

type Approval = {
  id: string;
  action: string;
  target: string;
  created_at: string;
  params: Record<string, unknown>;
};

const approvals: Approval[] = [
  {
    id: "a-1",
    action: "approve_leave",
    target: "HR Assistant",
    created_at: "19 Jun 2026",
    params: { employee: "MX0001", days: 1 },
  },
  {
    id: "a-2",
    action: "process_payment",
    target: "Finance Assistant",
    created_at: "19 Jun 2026",
    params: { amount: 15000, currency: "CNY", vendor: "Cloud Services" },
  },
  {
    id: "a-3",
    action: "create_user_account",
    target: "Onboarding Workflow",
    created_at: "18 Jun 2026",
    params: { email: "new.hire@mx.local", role: "employee" },
  },
  {
    id: "a-4",
    action: "revoke_access",
    target: "IT Assistant",
    created_at: "18 Jun 2026",
    params: { user: "former.employee@mx.local", scope: "all" },
  },
];

export function ApprovalsList() {
  const [filterOpen, setFilterOpen] = useState(false);
  const [filter, setFilter] = useState("View: All");
  const [decision, setDecision] = useState<Record<string, "approved" | "denied">>({});

  return (
    <div className="relative flex min-h-0 flex-1 flex-col px-5 py-5">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-semibold">Approvals</h1>
        <div className="relative">
          <CommandButton className="h-9 justify-between px-4 normal-case" onClick={() => setFilterOpen((open) => !open)}>
            <span>{filter}</span>
            <span className="ml-20 text-[9px]">▼</span>
          </CommandButton>
          {filterOpen ? (
            <div className="absolute right-0 top-11 z-20 w-48 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
              {["View: All", "Status: Pending", "Status: Approved", "Status: Denied"].map((option) => (
                <button
                  className={cn(
                    "flex h-9 w-full items-center rounded px-2 text-left text-sm hover:bg-neutral-100",
                    option === filter && "bg-neutral-100 font-medium",
                  )}
                  key={option}
                  onClick={() => {
                    setFilter(option);
                    setFilterOpen(false);
                  }}
                  type="button"
                >
                  {option}
                </button>
              ))}
            </div>
          ) : null}
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto pb-6">
        {approvals.map((approval) => (
          <article className="border-b border-neutral-100 px-4 py-5" key={approval.id}>
            <div className="grid gap-4 lg:grid-cols-[1fr_180px_140px]">
              <div>
                <p className="font-mono text-sm">{approval.action}</p>
                <p className="mt-3 text-sm text-neutral-500">
                  {Object.entries(approval.params)
                    .map(([key, value]) => `${key}: ${String(value)}`)
                    .join(", ")}
                </p>
                <div className="mt-4 flex gap-2">
                  <CommandButton
                    className={decision[approval.id] === "denied" ? "border-red-200 bg-red-50 text-red-700" : ""}
                    onClick={() => setDecision((current) => ({ ...current, [approval.id]: "denied" }))}
                  >
                    Deny
                  </CommandButton>
                  <CommandButton
                    className={decision[approval.id] === "approved" ? "border-emerald-200 bg-emerald-50 text-emerald-700" : ""}
                    onClick={() => setDecision((current) => ({ ...current, [approval.id]: "approved" }))}
                  >
                    Approve
                  </CommandButton>
                </div>
              </div>
              <div className="flex items-start gap-2 text-sm text-neutral-600">
                <span className="mt-1 size-2 rounded-full bg-[#ff3b25]" />
                {approval.target}
              </div>
              <p className="font-mono text-xs text-neutral-500">{approval.created_at}</p>
            </div>
          </article>
        ))}
      </div>

      <div className="pointer-events-none absolute inset-x-0 top-36 z-10 flex justify-center">
        <div className="pointer-events-auto w-full max-w-xl text-center">
          <div className="mb-8 inline-flex -space-x-2">
            <span className="grid size-9 -rotate-12 place-items-center rounded-xl border border-neutral-200 bg-white shadow-sm">
              <ShieldAlert className="size-5" />
            </span>
            <span className="grid size-9 rotate-12 place-items-center rounded-xl border border-red-100 bg-white text-[#ff3b25] shadow-sm">
              <ShieldAlert className="size-5" />
            </span>
          </div>
          <h2 className="text-3xl font-semibold">Admin access required</h2>
          <p className="mt-3 text-sm leading-6 text-neutral-500">
            Approval can only be viewed and managed by admins. Local preview keeps the actions visible for verification.
          </p>
          <CommandButton className="mt-6">
            Learn More
            <ExternalLink className="size-3.5" />
          </CommandButton>
        </div>
      </div>
    </div>
  );
}
