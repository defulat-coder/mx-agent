"use client";

import { ChevronDown, ExternalLink, ShieldAlert } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { TableResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type ApprovalStatus = "all" | "pending" | "approved" | "rejected";
type LocalDecision = "approved" | "rejected";

type StatusOption = {
  label: string;
  status: ApprovalStatus;
};

const statusOptions: StatusOption[] = [
  { label: "All", status: "all" },
  { label: "Pending", status: "pending" },
  { label: "Approved", status: "approved" },
  { label: "Rejected", status: "rejected" },
];

function asString(value: unknown) {
  return String(value ?? "");
}

function rowId(row: Record<string, unknown>, index: number) {
  return asString(row.id || `${row.action}-${index}`);
}

function rowStatus(row: Record<string, unknown>, decisions: Record<string, LocalDecision>, index: number): ApprovalStatus {
  const decision = decisions[rowId(row, index)];
  if (decision) {
    return decision;
  }

  if (row.status === "approved" || row.status === "rejected" || row.status === "pending") {
    return row.status;
  }

  return "pending";
}

function renderParams(value: unknown) {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return Object.entries(value as Record<string, unknown>)
      .map(([key, item]) => `${key}: ${String(item)}`)
      .join(", ");
  }

  return asString(value);
}

function updateQuery(status: ApprovalStatus) {
  const params = new URLSearchParams(window.location.search);
  params.set("status", status);
  params.set("page", "1");
  params.set("limit", "25");
  window.history.replaceState(null, "", `${window.location.pathname}?${params.toString()}`);
}

export function ApprovalsList({
  initialStatus = "all",
  table,
}: {
  initialStatus?: ApprovalStatus;
  table: TableResponse;
}) {
  const [filterOpen, setFilterOpen] = useState(false);
  const [status, setStatus] = useState<ApprovalStatus>(initialStatus);
  const [decisions, setDecisions] = useState<Record<string, LocalDecision>>({});

  useEffect(() => {
    updateQuery(status);
  }, [status]);

  const visibleRows = useMemo(() => {
    if (status === "all") {
      return table.rows;
    }

    return table.rows.filter((row, index) => rowStatus(row, decisions, index) === status);
  }, [decisions, status, table.rows]);

  const activeLabel = statusOptions.find((option) => option.status === status)?.label ?? "All";

  function decide(row: Record<string, unknown>, index: number, decision: LocalDecision) {
    setDecisions((current) => ({ ...current, [rowId(row, index)]: decision }));
  }

  return (
    <div className="relative flex min-h-0 flex-1 flex-col px-7 py-7">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-neutral-950">Approvals</h1>
        <div className="relative">
          <button
            className="flex h-9 w-[200px] items-center justify-between rounded-md border border-neutral-200 bg-white px-3 text-left text-sm text-neutral-950 shadow-sm hover:bg-neutral-50"
            onClick={() => setFilterOpen((open) => !open)}
            type="button"
          >
            <span>
              <span className="text-neutral-500">View:</span> {activeLabel}
            </span>
            <ChevronDown className="size-4 text-neutral-500" />
          </button>

          {filterOpen ? (
            <div className="absolute right-0 top-10 z-30 w-[200px] rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
              <div className="h-8 px-2 py-1.5 text-sm text-neutral-500">Status</div>
              {statusOptions.map((option) => {
                const active = option.status === status;

                return (
                  <button
                    className="flex h-9 w-full items-center gap-2 rounded px-2 text-sm text-neutral-900 hover:bg-neutral-50"
                    key={option.status}
                    onClick={() => {
                      setStatus(option.status);
                      setFilterOpen(false);
                    }}
                    type="button"
                  >
                    <span
                      className={cn(
                        "grid size-4 place-items-center rounded-full border",
                        active ? "border-neutral-950" : "border-neutral-300",
                      )}
                    >
                      {active ? <span className="size-2 rounded-full bg-neutral-950" /> : null}
                    </span>
                    <span>{option.label}</span>
                  </button>
                );
              })}
            </div>
          ) : null}
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto pb-8">
        <table className="w-full table-fixed border-collapse text-sm">
          <tbody>
            {visibleRows.map((approval, index) => {
              const currentStatus = rowStatus(approval, decisions, index);
              const isPending = currentStatus === "pending";

              return (
                <tr className="border-b border-neutral-100" key={rowId(approval, index)}>
                  <td className="px-4 py-5 align-top">
                    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_220px_150px]">
                      <div className="min-w-0">
                        <p className="truncate font-mono text-sm text-neutral-950">{asString(approval.action)}</p>
                        <p className="mt-3 truncate text-sm text-neutral-500">{renderParams(approval.params)}</p>
                        {isPending ? (
                          <div className="mt-4 flex gap-2">
                            <CommandButton
                              className="h-6 px-3"
                              onClick={() => decide(approval, index, "rejected")}
                            >
                              Deny
                            </CommandButton>
                            <CommandButton
                              className="h-6 px-3"
                              onClick={() => decide(approval, index, "approved")}
                            >
                              Approve
                            </CommandButton>
                          </div>
                        ) : (
                          <p
                            className={cn(
                              "mt-4 font-mono text-[11px] uppercase",
                              currentStatus === "approved" ? "text-emerald-700" : "text-red-700",
                            )}
                          >
                            {currentStatus}
                          </p>
                        )}
                      </div>
                      <p className="text-sm text-neutral-600">{asString(approval.target)}</p>
                      <p className="font-mono text-xs text-neutral-500">{asString(approval.created_at)}</p>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="pointer-events-none absolute inset-x-7 top-[126px] z-20 flex h-[390px] items-center justify-center bg-white/80 backdrop-blur-sm">
        <div className="pointer-events-auto w-full max-w-xl text-center">
          <div className="mb-7 inline-flex -space-x-2">
            <span className="grid size-9 -rotate-12 place-items-center rounded-xl border border-neutral-200 bg-white shadow-sm">
              <ShieldAlert className="size-5" />
            </span>
            <span className="grid size-9 rotate-12 place-items-center rounded-xl border border-red-100 bg-white text-[#ff3b25] shadow-sm">
              <ShieldAlert className="size-5" />
            </span>
          </div>
          <h2 className="text-3xl font-semibold text-neutral-950">Admin access required</h2>
          <p className="mt-3 text-sm leading-6 text-neutral-500">
            Approval can only be viewed and managed by admins. Demo OS users don&apos;t have access.
          </p>
          <a
            className="mt-6 inline-flex h-7 items-center justify-center gap-1.5 rounded-md border border-neutral-200 bg-neutral-50 px-3 font-mono text-[11px] uppercase tracking-normal text-neutral-900 transition-colors hover:bg-neutral-100"
            href="https://docs.agno.com/agent-os/approvals/overview"
          >
            Learn More
            <ExternalLink className="size-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
}
