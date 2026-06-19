"use client";

import { Bot, ChevronDown, ChevronLeft, ChevronRight, Circle, Users, Workflow } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { TableResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type SessionKind = "all" | "agent" | "team" | "workflow";

type SessionFilter = {
  icon: typeof Circle;
  label: string;
  type: SessionKind;
};

const filters: SessionFilter[] = [
  { icon: Circle, label: "All", type: "all" },
  { icon: Bot, label: "Agents", type: "agent" },
  { icon: Users, label: "Teams", type: "team" },
  { icon: Workflow, label: "Workflows", type: "workflow" },
];

const pageSize = 25;

function asString(value: unknown) {
  return String(value ?? "");
}

function normalizeKind(value: unknown): Exclude<SessionKind, "all"> {
  if (value === "agent" || value === "team" || value === "workflow") {
    return value;
  }

  return "team";
}

function formatRowId(row: Record<string, unknown>, index: number) {
  return asString(row.id || row.session_id || index);
}

function updateQuery(type: SessionKind, page: number) {
  const params = new URLSearchParams(window.location.search);
  params.set("sort_by", "updated_at_desc");
  params.set("type", type);
  params.set("page", String(page));
  params.set("limit", String(pageSize));
  window.history.replaceState(null, "", `${window.location.pathname}?${params.toString()}`);
}

export function SessionsPanel({
  initialPage = 1,
  initialType = "all",
  table,
}: {
  initialPage?: number;
  initialType?: SessionKind;
  table: TableResponse;
}) {
  const [filterOpen, setFilterOpen] = useState(false);
  const [type, setType] = useState<SessionKind>(initialType);
  const [page, setPage] = useState(initialPage);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(() => new Set());

  const filteredRows = useMemo(() => {
    if (type === "all") {
      return table.rows;
    }

    return table.rows.filter((row) => normalizeKind(row.type) === type);
  }, [table.rows, type]);

  const totalPages = Math.max(1, Math.ceil(filteredRows.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const visibleRows = filteredRows.slice((safePage - 1) * pageSize, safePage * pageSize);
  const activeFilter = filters.find((filter) => filter.type === type) ?? filters[0];

  useEffect(() => {
    updateQuery(type, safePage);
  }, [safePage, type]);

  function chooseFilter(nextType: SessionKind) {
    setType(nextType);
    setPage(1);
    setFilterOpen(false);
    setSelectedIds(new Set());
  }

  function toggleRow(rowId: string) {
    setSelectedIds((current) => {
      const next = new Set(current);
      if (next.has(rowId)) {
        next.delete(rowId);
      } else {
        next.add(rowId);
      }
      return next;
    });
  }

  function goToPage(nextPage: number) {
    setPage(Math.min(Math.max(nextPage, 1), totalPages));
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col px-7 py-7">
      <div className="mb-5 flex items-start justify-between gap-4">
        <nav aria-label="breadcrumb" className="flex items-center gap-7 text-sm">
          <div>
            <p className="mb-1 font-mono text-[11px] text-neutral-500">Database</p>
            <p className="font-medium text-neutral-950">{table.database}</p>
          </div>
          <div>
            <p className="mb-1 font-mono text-[11px] text-neutral-500">Table</p>
            <p className="font-medium text-neutral-950">{table.table}</p>
          </div>
        </nav>

        <div className="relative">
          <button
            className="flex h-9 w-44 items-center justify-between rounded-md border border-neutral-200 bg-white px-3 text-left text-sm text-neutral-950 shadow-sm hover:bg-neutral-50"
            onClick={() => setFilterOpen((open) => !open)}
            type="button"
          >
            <span>
              <span className="text-neutral-500">View:</span> {activeFilter.label}
            </span>
            <ChevronDown className="size-4 text-neutral-500" />
          </button>

          {filterOpen ? (
            <div className="absolute right-0 top-10 z-20 w-44 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
              {filters.map((filter) => {
                const Icon = filter.icon;
                const active = filter.type === type;

                return (
                  <button
                    className="flex h-9 w-full items-center gap-2 rounded px-2 text-sm text-neutral-900 hover:bg-neutral-50"
                    key={filter.type}
                    onClick={() => chooseFilter(filter.type)}
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
                    <Icon className="size-4 text-neutral-500" />
                    <span>{filter.label}</span>
                  </button>
                );
              })}
            </div>
          ) : null}
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto">
        <table className="w-full table-fixed border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-neutral-100 font-mono text-[11px] uppercase text-neutral-500">
              <th className="w-12 px-4 py-3 font-medium">
                <span className="block size-4 rounded border border-neutral-300" />
              </th>
              <th className="px-4 py-3 font-medium">Session Name</th>
              <th className="w-52 px-4 py-3 text-right font-medium">
                <button className="inline-flex items-center gap-1 uppercase" type="button">
                  Updated At
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row, index) => {
              const rowId = formatRowId(row, index);
              const selected = selectedIds.has(rowId);

              return (
                <tr
                  className="border-b border-neutral-100 text-neutral-700 hover:bg-neutral-50"
                  key={rowId}
                >
                  <td className="px-4 py-4">
                    <button
                      aria-label={`Select ${asString(row.name)}`}
                      aria-pressed={selected}
                      className={cn(
                        "grid size-4 place-items-center rounded border",
                        selected ? "border-neutral-950 bg-neutral-950" : "border-neutral-300 bg-white",
                      )}
                      onClick={() => toggleRow(rowId)}
                      type="button"
                    >
                      {selected ? <span className="size-1.5 rounded-sm bg-white" /> : null}
                    </button>
                  </td>
                  <td className="truncate px-4 py-4">{asString(row.name)}</td>
                  <td className="px-4 py-4 text-right text-neutral-600">{asString(row.updated_at)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {visibleRows.length === 0 ? (
          <div className="flex min-h-[360px] items-center justify-center text-center">
            <div>
              <h2 className="text-xl font-semibold text-neutral-950">No sessions logged</h2>
              <p className="mt-2 max-w-sm text-sm text-neutral-500">
                View sessions created by agents, teams and workflows.
              </p>
              <div className="mt-5 flex items-center justify-center gap-3">
                <a
                  className="inline-flex h-9 items-center justify-center rounded-md border border-neutral-200 px-4 font-mono text-[11px] uppercase text-neutral-950 hover:bg-neutral-50"
                  href="https://docs.agno.com/database/session-storage"
                >
                  Learn More
                </a>
                <a
                  className="inline-flex h-9 items-center justify-center rounded-md bg-neutral-950 px-4 font-mono text-[11px] uppercase text-white hover:bg-neutral-800"
                  href="/chat"
                >
                  Go To Chat Page
                </a>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      <div className="mt-5 flex items-center justify-center gap-3">
        <button
          aria-label="Previous page"
          className="grid size-9 place-items-center rounded-md border border-neutral-200 text-neutral-500 hover:bg-neutral-50 disabled:opacity-40"
          disabled={safePage <= 1}
          onClick={() => goToPage(safePage - 1)}
          type="button"
        >
          <ChevronLeft className="size-4" />
        </button>
        <input
          aria-label="Page"
          className="h-8 w-8 border-0 bg-transparent text-center text-sm outline-none"
          inputMode="numeric"
          onChange={(event) => goToPage(Number(event.target.value) || 1)}
          value={safePage}
        />
        <span className="text-sm text-neutral-500">/ {totalPages}</span>
        <button
          aria-label="Next page"
          className="grid size-9 place-items-center rounded-md border border-neutral-200 text-neutral-500 hover:bg-neutral-50 disabled:opacity-40"
          disabled={safePage >= totalPages}
          onClick={() => goToPage(safePage + 1)}
          type="button"
        >
          <ChevronRight className="size-4" />
        </button>
      </div>
    </div>
  );
}
