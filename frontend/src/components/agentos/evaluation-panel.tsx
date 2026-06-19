"use client";

import { ArrowDown, ChevronDown, Plus, RotateCcw, Save, Trash2, X } from "lucide-react";
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
  const [rerunId, setRerunId] = useState<string | null>(null);
  const displayDatabase = table.database === "mx-agent-db" ? "demo-os-db" : table.database;

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

  return (
    <div className="relative min-h-0 flex-1 overflow-hidden px-5 py-5">
      <div className={cn("flex min-h-0 flex-1 flex-col transition-[margin] duration-200", selectedRow && "mr-[628px]")}>
        <div className="mb-5 flex items-start justify-between gap-4">
          <div className="flex gap-6 text-sm">
            <div>
              <p className="mb-1 text-xs text-neutral-500">Database</p>
              <p className="whitespace-nowrap font-medium">{displayDatabase}</p>
            </div>
            <div className="pt-6 font-mono text-neutral-500">/</div>
            <div>
              <p className="mb-1 text-xs text-neutral-500">Table</p>
              <p className="whitespace-nowrap font-medium">{table.table}</p>
            </div>
          </div>

          <div className="relative">
            <CommandButton
              className="h-9 w-44 justify-between px-3 text-xs normal-case"
              onClick={() => {
                setScopeOpen((open) => !open);
                setTypeOpen(false);
              }}
            >
              <span>View: {scope}</span>
              <ChevronDown className="size-3.5" />
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
        </div>

        <div className="mb-3 flex items-center justify-between gap-4 border-t border-neutral-100 pt-3">
          <CommandButton
            className="h-9 cursor-not-allowed border-neutral-300 bg-neutral-500 px-4 text-xs text-white opacity-70 hover:bg-neutral-500"
            disabled
          >
            <Plus className="size-3.5" />
            New Eval
          </CommandButton>

          <div className="relative">
            <CommandButton
              className="h-9 w-[200px] justify-between px-3 text-xs normal-case"
              onClick={() => {
                setTypeOpen((open) => !open);
                setScopeOpen(false);
              }}
            >
              <span className="truncate">View: {typeFilter}</span>
              <ChevronDown className="size-3.5 shrink-0" />
            </CommandButton>
            {typeOpen ? (
              <div className="absolute right-0 top-11 z-30 w-60 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
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

        <div className="relative min-h-0 flex-1 overflow-hidden rounded-lg border border-neutral-200 bg-white">
          <div className="min-h-0 flex-1 overflow-auto">
            <table className="w-full min-w-[760px] border-collapse text-left text-sm">
              <thead>
                <tr className="h-12 border-b border-neutral-100 font-mono text-[11px] uppercase text-neutral-500">
                  <th className="w-12 px-4 font-medium">
                    <SelectionBox label="Select all evaluations" />
                  </th>
                  <th className="px-4 font-medium">Evaluation Name</th>
                  <th className="px-4 font-medium">Agent/Team</th>
                  <th className="px-4 font-medium">Model</th>
                  <th className="px-4 font-medium">Type</th>
                  <th className="px-4 font-medium">
                    <button
                      className="ml-auto flex items-center gap-1 uppercase"
                      onClick={() => setSortDesc((desc) => !desc)}
                      type="button"
                    >
                      Updated at
                      <ArrowDown className={cn("size-3 text-[#ff3b25]", !sortDesc && "rotate-180")} />
                    </button>
                  </th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => {
                  const id = String(row.id ?? index);
                  const selected = id === selectedId;
                  return (
                    <tr
                      className={cn(
                        "h-14 cursor-pointer border-b border-neutral-100 text-neutral-700 last:border-b-0 hover:bg-neutral-50",
                        selected && "bg-[#fff0ef] hover:bg-[#fff0ef]",
                      )}
                      key={id}
                      onClick={() => {
                        setScopeOpen(false);
                        setTypeOpen(false);
                        setSelectedId(selected ? null : id);
                      }}
                    >
                      <td className="px-4">
                        <SelectionBox label={`Select ${value(row, "name")}`} />
                      </td>
                      <td className="px-4 font-medium text-neutral-950">{value(row, "name")}</td>
                      <td className="px-4">
                        <span className="inline-flex items-center gap-2 font-semibold text-neutral-900">
                          <span className="size-4 rounded-[5px] border border-[#ff6b5b] shadow-[inset_0_0_0_3px_white]" />
                          {value(row, "target")}
                        </span>
                      </td>
                      <td className="px-4">
                        <span className="inline-flex items-center gap-2">
                          <span className="grid size-4 place-items-center rounded-full border border-neutral-500 font-mono text-[9px] leading-none">
                            ◎
                          </span>
                          {value(row, "model")}
                        </span>
                      </td>
                      <td className="px-4 text-neutral-600">{value(row, "type")}</td>
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
      </div>

      {selectedRow ? (
        <EvaluationInspector
          onClose={() => setSelectedId(null)}
          onRerun={() => {
            setRerunId(String(selectedRow.id));
            window.setTimeout(() => setRerunId(null), 1400);
          }}
          rerunning={rerunId === String(selectedRow.id)}
          row={selectedRow}
        />
      ) : null}
    </div>
  );
}

function SelectionBox({ label }: { label: string }) {
  return (
    <button
      aria-label={label}
      className="grid size-4 place-items-center rounded border border-neutral-900 bg-white shadow-sm"
      onClick={(event) => event.stopPropagation()}
      type="button"
    />
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
    <div className="absolute right-0 top-11 z-30 w-44 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
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
      className={cn(
        "flex h-9 w-full items-center rounded px-2 text-left text-sm hover:bg-neutral-100",
        selected && "bg-neutral-100 font-medium",
      )}
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
    <aside className="absolute bottom-4 right-4 top-[119px] flex w-[620px] flex-col overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-[0_10px_28px_rgba(0,0,0,0.08)]">
      <div className="flex items-start justify-between px-6 py-7">
        <h2 className="min-w-0 text-xl font-medium leading-7">
          {value(row, "name")} <span className="font-normal text-neutral-600">{value(row, "target")} using</span>{" "}
          <span className="font-semibold">{value(row, "model")}</span>
        </h2>
        <button
          aria-label="Close details"
          className="ml-4 grid size-9 shrink-0 place-items-center rounded-lg border border-neutral-200 text-neutral-600 hover:bg-neutral-100"
          onClick={onClose}
          type="button"
        >
          <X className="size-4" />
        </button>
      </div>

      <div className="mx-6 grid grid-cols-5 overflow-hidden rounded-lg border border-neutral-200 text-center">
        {[
          ["AVG SCORE", "avg_score"],
          ["MAX SCORE", "max_score"],
          ["MIN SCORE", "min_score"],
          ["MEAN SCORE", "mean_score"],
          ["STD DEV SCORE", "std_dev_score"],
        ].map(([label, key]) => (
          <div className="border-r border-neutral-200 px-2 py-3 last:border-r-0" key={key}>
            <p className="font-mono text-[10px] uppercase leading-4 text-neutral-500">{label}</p>
            <p className="mt-3 text-sm font-medium">{numberValue(row, key)}</p>
          </div>
        ))}
      </div>

      <div className="min-h-0 flex-1 overflow-auto px-6 py-6 pb-24">
        <div className="rounded-lg border border-neutral-200">
          <div className="flex h-16 items-center justify-between border-b border-neutral-100 px-4">
            <h3 className="text-xl font-medium">Results</h3>
            <ChevronDown className="size-4 rotate-180 text-neutral-600" />
          </div>
          <ResultField label="Score" value={String(details.score ?? value(row, "avg_score"))} />
          <ResultField label="Output" value={String(details.output ?? "-")} />
          <ResultField label="Expected Output" value={String(details.expected_output ?? "-")} />
          <ResultField label="Input" value={String(details.input ?? "-")} />
          <ResultField label="Reason" value={String(details.reason ?? "-")} />
        </div>
      </div>

      <div className="absolute inset-x-0 bottom-0 flex items-center justify-end gap-2 border-t border-neutral-200 bg-neutral-50 px-5 py-4">
        <CommandButton className="border-red-200 bg-red-50 text-red-700 hover:bg-red-100">
          <Trash2 className="size-3.5" />
          Delete
        </CommandButton>
        <CommandButton
          className={cn("cursor-not-allowed text-neutral-400", rerunning && "border-emerald-200 bg-emerald-50 text-emerald-700")}
          disabled
          onClick={onRerun}
        >
          <RotateCcw className="size-3.5" />
          {rerunning ? "Queued" : "ReRun"}
        </CommandButton>
        <CommandButton onClick={onClose}>Close</CommandButton>
        <CommandButton className="cursor-not-allowed opacity-80" disabled tone="dark">
          <Save className="size-3.5" />
          Save
        </CommandButton>
      </div>
    </aside>
  );
}

function ResultField({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[96px_1fr] border-b border-neutral-200 px-4 py-4 last:border-b-0">
      <p className="font-mono text-[10px] uppercase leading-5 text-neutral-500">{label}</p>
      <p className="text-sm leading-6 text-neutral-800">{value}</p>
    </div>
  );
}
