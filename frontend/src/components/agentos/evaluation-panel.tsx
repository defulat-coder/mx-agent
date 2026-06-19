"use client";

import {
  ClipboardCheck,
  Download,
  Filter,
  PanelRightClose,
  Plus,
  RotateCcw,
  Save,
  Trash2,
} from "lucide-react";
import { useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { TableResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type EvaluationRow = Record<string, unknown>;

const scopeOptions = ["All", "Agents", "Teams"];
const typeOptions = ["Select all", "Accuracy", "Performance", "Reliability", "Agent As Judge", "gpt-5.5"];

function value(row: EvaluationRow, key: string, fallback = "-") {
  const raw = row[key];
  return typeof raw === "string" || typeof raw === "number" ? String(raw) : fallback;
}

function numberValue(row: EvaluationRow, key: string, fallback = "0.00") {
  const raw = row[key];
  return typeof raw === "number" ? raw.toFixed(2) : typeof raw === "string" ? raw : fallback;
}

function result(row: EvaluationRow) {
  const raw = row.result;
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    return raw as Record<string, string | number>;
  }
  return {};
}

export function EvaluationPanel({ table }: { table: TableResponse }) {
  const [scopeOpen, setScopeOpen] = useState(false);
  const [typeOpen, setTypeOpen] = useState(false);
  const [scope, setScope] = useState("All");
  const [typeFilter, setTypeFilter] = useState("All evaluations");
  const [sortDesc, setSortDesc] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [newEvalOpen, setNewEvalOpen] = useState(false);
  const [exported, setExported] = useState(false);
  const [rerunId, setRerunId] = useState<string | null>(null);

  const rows = useMemo(() => {
    const filtered = table.rows.filter((row) => {
      const kind = value(row, "kind").toLowerCase();
      const type = value(row, "type").toLowerCase();
      const model = value(row, "model").toLowerCase();
      const scopeMatch =
        scope === "All" || (scope === "Agents" && kind === "agent") || (scope === "Teams" && kind === "team");
      const typeMatch =
        typeFilter === "All evaluations" ||
        type === typeFilter.toLowerCase() ||
        model === typeFilter.toLowerCase();
      return scopeMatch && typeMatch;
    });
    return sortDesc ? filtered : [...filtered].reverse();
  }, [scope, sortDesc, table.rows, typeFilter]);

  const selectedRow = useMemo(
    () => table.rows.find((row, index) => String(row.id ?? index) === selectedId) ?? null,
    [selectedId, table.rows],
  );

  const sidePanel = newEvalOpen ? (
    <NewEvaluationPanel onClose={() => setNewEvalOpen(false)} />
  ) : selectedRow ? (
    <EvaluationInspector
      onClose={() => setSelectedId(null)}
      onRerun={() => {
        setRerunId(String(selectedRow.id));
        window.setTimeout(() => setRerunId(null), 1400);
      }}
      rerunning={rerunId === String(selectedRow.id)}
      row={selectedRow}
    />
  ) : null;

  return (
    <div className="flex min-h-0 flex-1 overflow-hidden">
      <div className="flex min-w-0 flex-1 flex-col px-5 py-5">
        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">Evaluation</h1>
            <div className="mt-5 flex gap-6 text-sm">
              <div>
                <p className="mb-1 text-xs text-neutral-500">Database</p>
                <p className="whitespace-nowrap font-medium">{table.database}</p>
              </div>
              <div className="pt-6 font-mono text-neutral-500">/</div>
              <div>
                <p className="mb-1 text-xs text-neutral-500">Table</p>
                <p className="whitespace-nowrap font-medium">{table.table}</p>
              </div>
            </div>
          </div>

          <div className="relative flex flex-wrap items-center justify-end gap-2">
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
            <div className="relative">
              <CommandButton
                className="h-9 justify-between px-4 normal-case"
                onClick={() => {
                  setScopeOpen((open) => !open);
                  setTypeOpen(false);
                }}
              >
                <Filter className="size-3.5" />
                <span>View: {scope}</span>
                <span className="ml-8 text-[9px]">▼</span>
              </CommandButton>
              {scopeOpen ? (
                <FilterMenu
                  options={scopeOptions}
                  selected={scope}
                  onSelect={(option) => {
                    setScope(option);
                    setScopeOpen(false);
                  }}
                />
              ) : null}
            </div>
            <CommandButton
              className="h-9 px-4"
              onClick={() => {
                setNewEvalOpen(true);
                setSelectedId(null);
              }}
              tone="dark"
            >
              <Plus className="size-3.5" />
              New Eval
            </CommandButton>
            <div className="relative">
              <CommandButton
                className="h-9 justify-between px-4 normal-case"
                onClick={() => {
                  setTypeOpen((open) => !open);
                  setScopeOpen(false);
                }}
              >
                <Filter className="size-3.5" />
                <span>View: {typeFilter}</span>
                <span className="ml-8 text-[9px]">▼</span>
              </CommandButton>
              {typeOpen ? (
                <div className="absolute right-0 top-11 z-20 w-60 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
                  <p className="px-2 py-1.5 font-mono text-[10px] uppercase text-neutral-500">Types</p>
                  {typeOptions.slice(0, 5).map((option) => (
                    <FilterOption
                      key={option}
                      option={option}
                      selected={option === "Select all" ? typeFilter === "All evaluations" : typeFilter === option}
                      onClick={() => {
                        setTypeFilter(option === "Select all" ? "All evaluations" : option);
                        setTypeOpen(false);
                      }}
                    />
                  ))}
                  <p className="px-2 py-1.5 font-mono text-[10px] uppercase text-neutral-500">Models</p>
                  <FilterOption
                    option="gpt-5.5"
                    selected={typeFilter === "gpt-5.5"}
                    onClick={() => {
                      setTypeFilter("gpt-5.5");
                      setTypeOpen(false);
                    }}
                  />
                </div>
              ) : null}
            </div>
          </div>
        </div>

        <div className="relative min-h-0 flex-1 overflow-auto">
          <table className="min-w-[920px] w-full border-collapse text-left text-sm">
            <thead>
              <tr className="sticky top-0 z-10 h-12 border-b border-neutral-100 bg-neutral-50 font-mono text-[11px] uppercase text-neutral-500">
                {table.columns.map((column) => (
                  <th className="px-4 font-medium" key={column.key}>
                    {column.key === "updated_at" ? (
                      <button
                        className="flex items-center gap-1 uppercase"
                        onClick={() => setSortDesc((desc) => !desc)}
                        type="button"
                      >
                        {column.label}
                        <span className="text-[9px]">{sortDesc ? "↓" : "↑"}</span>
                      </button>
                    ) : (
                      column.label
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => {
                const id = String(row.id ?? index);
                const selected = id === selectedId;
                return (
                  <tr
                    className={cn(
                      "h-14 cursor-pointer border-b border-neutral-100 text-neutral-700 hover:bg-neutral-50",
                      selected && "bg-neutral-50",
                    )}
                    key={id}
                    onClick={() => {
                      setScopeOpen(false);
                      setTypeOpen(false);
                      setNewEvalOpen(false);
                      setSelectedId(selected ? null : id);
                    }}
                  >
                    <td className="px-4 font-medium text-neutral-900">{value(row, "name")}</td>
                    <td className="px-4 font-mono text-xs">{value(row, "target")}</td>
                    <td className="px-4 font-mono text-xs">{value(row, "model")}</td>
                    <td className="px-4">{value(row, "type")}</td>
                    <td className="px-4 text-neutral-600">{value(row, "updated_at")}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {rows.length === 0 ? (
            <div className="absolute inset-0 grid place-items-center">
              <div className="text-center">
                <p className="text-2xl font-semibold">No evaluations found</p>
                <p className="mt-2 text-sm text-neutral-500">Change the selected view or evaluation type.</p>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {sidePanel}
    </div>
  );
}

function FilterMenu({
  onSelect,
  options,
  selected,
}: {
  onSelect: (option: string) => void;
  options: string[];
  selected: string;
}) {
  return (
    <div className="absolute right-0 top-11 z-20 w-44 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
      {options.map((option) => (
        <FilterOption key={option} onClick={() => onSelect(option)} option={option} selected={selected === option} />
      ))}
    </div>
  );
}

function FilterOption({
  onClick,
  option,
  selected,
}: {
  onClick: () => void;
  option: string;
  selected: boolean;
}) {
  return (
    <button
      className={cn("flex h-9 w-full items-center rounded px-2 text-left text-sm hover:bg-neutral-100", selected && "bg-neutral-100 font-medium")}
      onClick={onClick}
      type="button"
    >
      {option}
    </button>
  );
}

function EvaluationInspector({
  onClose,
  onRerun,
  rerunning,
  row,
}: {
  onClose: () => void;
  onRerun: () => void;
  rerunning: boolean;
  row: EvaluationRow;
}) {
  const details = result(row);

  return (
    <aside className="flex w-[500px] shrink-0 flex-col border-l border-neutral-200 bg-white">
      <div className="flex items-start justify-between border-b border-neutral-100 px-5 py-4">
        <div>
          <p className="font-mono text-[11px] uppercase text-neutral-500">{value(row, "target")} using {value(row, "model")}</p>
          <h2 className="mt-1 text-base font-semibold">{value(row, "name")}</h2>
        </div>
        <button
          aria-label="Close details"
          className="grid size-7 place-items-center rounded-md text-neutral-500 hover:bg-neutral-100"
          onClick={onClose}
          type="button"
        >
          <PanelRightClose className="size-4" />
        </button>
      </div>

      <div className="grid grid-cols-5 border-b border-neutral-100 text-center">
        {[
          ["AVG SCORE", "avg_score"],
          ["MAX SCORE", "max_score"],
          ["MIN SCORE", "min_score"],
          ["MEAN SCORE", "mean_score"],
          ["STD DEV SCORE", "std_dev_score"],
        ].map(([label, key]) => (
          <div className="border-r border-neutral-100 px-2 py-4 last:border-r-0" key={key}>
            <p className="font-mono text-[10px] uppercase text-neutral-500">{label}</p>
            <p className="mt-2 text-xl font-semibold">{numberValue(row, key)}</p>
          </div>
        ))}
      </div>

      <div className="min-h-0 flex-1 overflow-auto px-5 py-4">
        <div className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase text-neutral-500">
          <ClipboardCheck className="size-3.5" />
          Results
        </div>
        <div className="rounded-md border border-neutral-200">
          <ResultField label="Score" value={String(details.score ?? value(row, "avg_score"))} />
          <ResultField label="Output" value={String(details.output ?? "-")} />
          <ResultField label="Expected Output" value={String(details.expected_output ?? "-")} />
          <ResultField label="Input" value={String(details.input ?? "-")} />
          <ResultField label="Reason" value={String(details.reason ?? "-")} />
        </div>
      </div>

      <div className="flex items-center justify-end gap-2 border-t border-neutral-100 px-5 py-4">
        <CommandButton className="border-red-200 bg-red-50 text-red-700 hover:bg-red-100">
          <Trash2 className="size-3.5" />
          Delete
        </CommandButton>
        <CommandButton
          className={cn(rerunning && "border-emerald-200 bg-emerald-50 text-emerald-700")}
          onClick={onRerun}
        >
          <RotateCcw className="size-3.5" />
          {rerunning ? "Queued" : "ReRun"}
        </CommandButton>
        <CommandButton onClick={onClose}>Close</CommandButton>
        <CommandButton tone="dark">
          <Save className="size-3.5" />
          Save
        </CommandButton>
      </div>
    </aside>
  );
}

function ResultField({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-b border-neutral-200 px-4 py-3 last:border-b-0">
      <p className="mb-1 font-mono text-[10px] uppercase text-neutral-500">{label}</p>
      <p className="text-sm leading-6 text-neutral-800">{value}</p>
    </div>
  );
}

function NewEvaluationPanel({ onClose }: { onClose: () => void }) {
  return (
    <aside className="flex w-[420px] shrink-0 flex-col border-l border-neutral-200 bg-white">
      <div className="flex items-start justify-between border-b border-neutral-100 px-5 py-4">
        <div>
          <p className="font-mono text-[11px] uppercase text-neutral-500">Evaluation</p>
          <h2 className="mt-1 text-base font-semibold">New Eval</h2>
        </div>
        <button
          aria-label="Close new evaluation"
          className="grid size-7 place-items-center rounded-md text-neutral-500 hover:bg-neutral-100"
          onClick={onClose}
          type="button"
        >
          <PanelRightClose className="size-4" />
        </button>
      </div>

      <div className="flex-1 space-y-4 px-5 py-4">
        {[
          ["Evaluation Name", "Policy regression"],
          ["Agent/Team", "router-team"],
          ["Model", "gpt-5.5"],
          ["Type", "Accuracy"],
        ].map(([label, placeholder]) => (
          <label className="block" key={label}>
            <span className="mb-1 block font-mono text-[10px] uppercase text-neutral-500">{label}</span>
            <input
              className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-neutral-400"
              placeholder={placeholder}
            />
          </label>
        ))}
        <label className="block">
          <span className="mb-1 block font-mono text-[10px] uppercase text-neutral-500">Prompt</span>
          <textarea
            className="min-h-28 w-full resize-none rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
            placeholder="What should this evaluation validate?"
          />
        </label>
      </div>

      <div className="flex items-center justify-end gap-2 border-t border-neutral-100 px-5 py-4">
        <CommandButton onClick={onClose}>Close</CommandButton>
        <CommandButton tone="dark">
          <Plus className="size-3.5" />
          Create
        </CommandButton>
      </div>
    </aside>
  );
}
