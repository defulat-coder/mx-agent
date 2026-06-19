"use client";

import { CalendarClock, Download, Filter, PanelRightClose, Play, Power, RotateCcw } from "lucide-react";
import { useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { TableResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type ScheduleRow = Record<string, unknown>;

function text(row: ScheduleRow, key: string, fallback = "-") {
  const value = row[key];
  return typeof value === "string" || typeof value === "number" ? String(value) : fallback;
}

function enabledValue(row: ScheduleRow) {
  return row.enabled === true || row.enabled === "true";
}

export function SchedulerPanel({ table }: { table: TableResponse }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filterOpen, setFilterOpen] = useState(false);
  const [filter, setFilter] = useState("View: All");
  const [exported, setExported] = useState(false);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [enabledById, setEnabledById] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(table.rows.map((row, index) => [String(row.id ?? index), enabledValue(row)])),
  );

  const rows = useMemo(() => {
    if (filter === "Enabled") {
      return table.rows.filter((row, index) => enabledById[String(row.id ?? index)]);
    }
    if (filter === "Disabled") {
      return table.rows.filter((row, index) => !enabledById[String(row.id ?? index)]);
    }
    return table.rows;
  }, [enabledById, filter, table.rows]);

  const selectedRow = useMemo(
    () => table.rows.find((row, index) => String(row.id ?? index) === selectedId) ?? null,
    [selectedId, table.rows],
  );

  return (
    <div className="flex min-h-0 flex-1 overflow-hidden">
      <div className="flex min-w-0 flex-1 flex-col px-5 py-5">
        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">Scheduler</h1>
            <div className="mt-5 flex gap-6 text-sm">
              <div>
                <p className="mb-1 text-xs text-neutral-500">Database</p>
                <p className="font-medium">{table.database}</p>
              </div>
              <div className="pt-6 font-mono text-neutral-500">/</div>
              <div>
                <p className="mb-1 text-xs text-neutral-500">Table</p>
                <p className="font-medium">{table.table}</p>
              </div>
            </div>
          </div>
          <div className="relative flex items-center gap-2">
            <CommandButton
              className={cn("h-9 px-4", exported && "border-emerald-200 bg-emerald-50 text-emerald-700")}
              onClick={() => {
                setExported(true);
                window.setTimeout(() => setExported(false), 1400);
              }}
            >
              <Download className="size-3.5" />
              {exported ? "Exported" : "Export"}
            </CommandButton>
            <CommandButton className="h-9 justify-between px-4 normal-case" onClick={() => setFilterOpen((open) => !open)}>
              <Filter className="size-3.5" />
              <span>{filter}</span>
              <span className="ml-10 text-[9px]">▼</span>
            </CommandButton>
            {filterOpen ? (
              <div className="absolute right-0 top-11 z-20 w-44 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
                {["View: All", "Enabled", "Disabled"].map((option) => (
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

        <div className="min-h-0 flex-1 overflow-auto">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-neutral-100 text-[11px] text-neutral-500">
                <th className="w-20 px-4 py-3 font-mono font-medium">ENABLED</th>
                <th className="px-4 py-3 font-mono font-medium">NAME</th>
                <th className="px-4 py-3 font-mono font-medium">CRON</th>
                <th className="px-4 py-3 font-mono font-medium">ENDPOINT</th>
                <th className="px-4 py-3 font-mono font-medium">NEXT RUN</th>
                <th className="px-4 py-3 font-mono font-medium">UPDATED AT</th>
                <th className="w-28 px-4 py-3 font-mono font-medium">ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => {
                const id = String(row.id ?? index);
                const enabled = enabledById[id];
                const selected = selectedId === id;

                return (
                  <tr
                    className={cn("cursor-pointer border-b border-neutral-100 text-neutral-700 hover:bg-neutral-50", selected && "bg-neutral-50")}
                    key={id}
                    onClick={() => {
                      setFilterOpen(false);
                      setSelectedId(selected ? null : id);
                    }}
                  >
                    <td className="px-4 py-4">
                      <Toggle
                        checked={enabled}
                        onToggle={() => {
                          setEnabledById((current) => ({ ...current, [id]: !enabled }));
                        }}
                      />
                    </td>
                    <td className="px-4 py-4 font-medium">{text(row, "name")}</td>
                    <td className="px-4 py-4 font-mono text-xs">{text(row, "cron")}</td>
                    <td className="px-4 py-4 font-mono text-xs">{text(row, "endpoint")}</td>
                    <td className="px-4 py-4 text-neutral-600">{text(row, "next_run")}</td>
                    <td className="px-4 py-4 text-neutral-500">{text(row, "updated_at")}</td>
                    <td className="px-4 py-4">
                      <button
                        className={cn(
                          "inline-flex h-8 items-center gap-2 rounded-md border border-neutral-200 px-3 font-mono text-[11px] uppercase hover:bg-neutral-100",
                          runningId === id && "border-emerald-200 bg-emerald-50 text-emerald-700",
                        )}
                        onClick={(event) => {
                          event.stopPropagation();
                          setRunningId(id);
                          window.setTimeout(() => setRunningId(null), 1600);
                        }}
                        type="button"
                      >
                        <Play className="size-3.5" />
                        {runningId === id ? "Queued" : "Run"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {rows.length === 0 ? (
            <div className="grid h-80 place-items-center text-center">
              <div>
                <h2 className="text-2xl font-semibold">No schedules found</h2>
                <p className="mt-2 text-sm text-neutral-500">Change the current view to see other schedules.</p>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {selectedRow ? (
        <ScheduleInspector
          enabled={enabledById[String(selectedRow.id ?? 0)]}
          onClose={() => setSelectedId(null)}
          row={selectedRow}
          running={runningId === String(selectedRow.id ?? 0)}
          setRunning={() => {
            const id = String(selectedRow.id ?? 0);
            setRunningId(id);
            window.setTimeout(() => setRunningId(null), 1600);
          }}
        />
      ) : null}
    </div>
  );
}

function Toggle({ checked, onToggle }: { checked: boolean; onToggle: () => void }) {
  return (
    <button
      aria-label={checked ? "Disable schedule" : "Enable schedule"}
      aria-pressed={checked}
      className={cn(
        "relative h-6 w-11 rounded-full border border-neutral-200 bg-neutral-200 transition-colors",
        checked && "border-neutral-900 bg-neutral-900",
      )}
      onClick={(event) => {
        event.stopPropagation();
        onToggle();
      }}
      type="button"
    >
      <span
        className={cn(
          "absolute left-0.5 top-0.5 size-5 rounded-full bg-white shadow-sm transition-transform",
          checked && "translate-x-5",
        )}
      />
    </button>
  );
}

function ScheduleInspector({
  enabled,
  onClose,
  row,
  running,
  setRunning,
}: {
  enabled: boolean;
  onClose: () => void;
  row: ScheduleRow;
  running: boolean;
  setRunning: () => void;
}) {
  return (
    <aside className="w-[420px] shrink-0 border-l border-neutral-200 bg-white px-4 py-5">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="font-mono text-[11px] uppercase text-neutral-500">Schedule</p>
          <h2 className="mt-1 text-sm font-semibold">{text(row, "name")}</h2>
        </div>
        <button
          aria-label="Close schedule details"
          className="grid size-7 place-items-center rounded-md text-neutral-500 hover:bg-neutral-100"
          onClick={onClose}
          type="button"
        >
          <PanelRightClose className="size-4" />
        </button>
      </div>

      <div className="rounded-lg bg-neutral-50 p-4">
        <div className="mb-4 flex items-center gap-2">
          <span className={cn("grid size-8 place-items-center rounded-md", enabled ? "bg-neutral-950 text-white" : "bg-neutral-200 text-neutral-500")}>
            <Power className="size-4" />
          </span>
          <div>
            <p className="text-sm font-medium">{enabled ? "Enabled" : "Disabled"}</p>
            <p className="text-xs text-neutral-500">Local scheduler state</p>
          </div>
        </div>
        <InspectorItem label="Cron" value={text(row, "cron")} />
        <InspectorItem label="Endpoint" value={text(row, "endpoint")} />
        <InspectorItem label="Next run" value={text(row, "next_run")} />
        <InspectorItem label="Updated at" value={text(row, "updated_at")} />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2">
        <CommandButton className={cn("h-9", running && "border-emerald-200 bg-emerald-50 text-emerald-700")} onClick={setRunning}>
          <Play className="size-3.5" />
          {running ? "Queued" : "Run now"}
        </CommandButton>
        <CommandButton className="h-9">
          <RotateCcw className="size-3.5" />
          Refresh
        </CommandButton>
      </div>

      <div className="mt-5 rounded-lg border border-neutral-200 p-4">
        <div className="mb-3 flex items-center gap-2">
          <CalendarClock className="size-4 text-neutral-500" />
          <h3 className="text-sm font-semibold">Execution window</h3>
        </div>
        <p className="text-sm leading-6 text-neutral-600">
          This job will call the configured endpoint on the next cron tick. Runtime logs are linked from Traces after execution.
        </p>
      </div>
    </aside>
  );
}

function InspectorItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-b border-neutral-200/70 py-3 last:border-0">
      <p className="mb-1 font-mono text-[11px] uppercase text-neutral-500">{label}</p>
      <p className="font-mono text-xs text-neutral-800">{value}</p>
    </div>
  );
}
