"use client";

import {
  AlertTriangle,
  Check,
  ChevronLeft,
  CircleDot,
  Code2,
  Copy,
  Download,
  ExternalLink,
  Filter,
  MessageSquare,
  PanelRightOpen,
} from "lucide-react";
import { useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { TableResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type TraceTab = "info" | "metadata";
type TextMode = "text" | "formatted";

const traceSpans = [
  { name: "RouterTeam.arun", kind: "agent", duration: "4.93s", tokens: null, depth: 0 },
  { name: "input_validation", kind: "tool", duration: "45ms", tokens: null, depth: 1 },
  { name: "policy_context_fetch", kind: "tool", duration: "312ms", tokens: null, depth: 1 },
  { name: "OpenAIChat.ainvoke_stream", kind: "model", duration: "1.53s", tokens: 17, depth: 1 },
  { name: "HR Assistant.arun", kind: "agent", duration: "1.12s", tokens: 22, depth: 1 },
  { name: "IT Assistant.arun", kind: "agent", duration: "845ms", tokens: null, depth: 2 },
  { name: "approval_policy_check", kind: "tool", duration: "298ms", tokens: null, depth: 2 },
  { name: "format_router_response", kind: "tool", duration: "156ms", tokens: null, depth: 1 },
  { name: "performance_metrics", kind: "tool", duration: "34ms", tokens: null, depth: 1 },
];

function value(row: Record<string, unknown>, key: string, fallback: string) {
  const field = row[key];
  return typeof field === "string" || typeof field === "number" ? String(field) : fallback;
}

function StatusBadge({ status }: { status: string }) {
  const error = status.toLowerCase() === "error";
  return (
    <span
      className={cn(
        "inline-flex h-7 items-center gap-1 rounded-md px-2 font-mono text-[11px] uppercase",
        error ? "bg-red-50 text-red-600" : "bg-neutral-100 text-neutral-700",
      )}
    >
      {error ? <AlertTriangle className="size-3.5" /> : <Check className="size-3.5" />}
      {status}
    </span>
  );
}

export function TraceExplorer({ table }: { table: TableResponse }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filterOpen, setFilterOpen] = useState(false);
  const [filter, setFilter] = useState("Group by: sessions");
  const [exported, setExported] = useState(false);

  const selectedRow = useMemo(
    () => table.rows.find((row, index) => String(row.id ?? index) === selectedId) ?? null,
    [selectedId, table.rows],
  );

  if (selectedRow) {
    return <TraceDetail database={table.database} onBack={() => setSelectedId(null)} row={selectedRow} />;
  }

  return (
    <div className="relative flex min-h-0 flex-1 flex-col overflow-hidden px-5 py-5">
      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          <p className="mb-1 text-xs text-neutral-500">Database</p>
          <p className="font-medium">{table.database}</p>
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
            <div className="absolute right-0 top-11 z-20 w-56 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
              {["Group by: sessions", "Group by: traces", "Status: OK", "Status: Error"].map((option) => (
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
              <th className="w-12 px-4 py-3 font-mono font-medium">
                <span className="block size-4 rounded border border-neutral-300" />
              </th>
              {table.columns.map((column) => (
                <th className="px-4 py-3 font-mono font-medium" key={column.key}>
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, index) => {
              const id = String(row.id ?? index);
              return (
                <tr
                  className="cursor-pointer border-b border-neutral-100 text-neutral-700 hover:bg-neutral-50"
                  key={id}
                  onClick={() => {
                    setFilterOpen(false);
                    setSelectedId(id);
                  }}
                >
                  <td className="px-4 py-4">
                    <span className="block size-4 rounded border border-neutral-300" />
                  </td>
                  {table.columns.map((column) => (
                    <td className={cn("px-4 py-4 align-middle", column.mono && "font-mono text-xs")} key={column.key}>
                      {column.key === "status" ? <StatusBadge status={value(row, column.key, "OK")} /> : value(row, column.key, "-")}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {table.rows.length === 0 ? <TracesEmptyOverlay /> : null}
    </div>
  );
}

function TraceDetail({
  database,
  onBack,
  row,
}: {
  database: string;
  onBack: () => void;
  row: Record<string, unknown>;
}) {
  const [selectedSpan, setSelectedSpan] = useState(traceSpans[0].name);
  const [traceTab, setTraceTab] = useState<TraceTab>("info");
  const [inputMode, setInputMode] = useState<TextMode>("formatted");
  const [outputMode, setOutputMode] = useState<TextMode>("formatted");
  const selected = traceSpans.find((span) => span.name === selectedSpan) ?? traceSpans[0];
  const input = value(row, "input", "What can you do?");
  const traceId = value(row, "trace_id", "9c645fe9dc507efba986d9f6e369b827");

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-auto px-5 py-5">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <p className="mb-1 text-xs text-neutral-500">Database</p>
          <p className="font-medium">{database}</p>
        </div>
        <CommandButton className="h-9" onClick={onBack}>
          <ChevronLeft className="size-3.5" />
          All traces
        </CommandButton>
      </div>

      <div className="grid min-h-[620px] gap-3 xl:grid-cols-[44%_1fr]">
        <section className="min-h-0 overflow-hidden rounded-lg border border-neutral-200 bg-white">
          <div className="grid grid-cols-2 border-b border-neutral-100 p-4 text-sm">
            <MetaItem label="Created at" value={value(row, "created_at", "19 Jun 2026, 09:31")} />
            <MetaItem label="Trace ID" mono value={traceId} />
            <MetaItem label="Run ID" mono value={value(row, "run_id", "af2bbb00-71ed-452b-aef2-3dfad4930462")} />
            <MetaItem label="Session ID" mono value={value(row, "session_id", "preview-session")} />
            <MetaItem label="User ID" mono value={value(row, "user_id", "operator@mx.local")} />
            <MetaItem label="Status" value={value(row, "status", "OK")} />
          </div>
          <div className="flex h-[450px] flex-col">
            <div className="flex items-center justify-between border-b border-neutral-100 px-4 py-3">
              <div>
                <h2 className="text-sm font-semibold">Trace Tree</h2>
                <p className="font-mono text-[11px] uppercase text-neutral-500">{value(row, "spans", "18")} spans</p>
              </div>
              <StatusBadge status={value(row, "status", "OK")} />
            </div>
            <div className="min-h-0 flex-1 overflow-auto p-3">
              {traceSpans.map((span) => (
                <button
                  className={cn(
                    "grid w-full grid-cols-[1fr_auto] items-center gap-3 rounded-md px-3 py-2 text-left text-sm hover:bg-neutral-50",
                    span.name === selectedSpan && "bg-neutral-100",
                  )}
                  key={`${span.name}-${span.duration}`}
                  onClick={() => setSelectedSpan(span.name)}
                  style={{ paddingLeft: `${12 + span.depth * 22}px` }}
                  type="button"
                >
                  <span className="flex min-w-0 items-center gap-2">
                    <SpanIcon kind={span.kind} />
                    <span className="truncate">{span.name}</span>
                  </span>
                  <span className="flex items-center gap-2 font-mono text-xs text-neutral-500">
                    {span.duration}
                    {span.tokens ? <span className="inline-flex items-center gap-1">⊙ {span.tokens}</span> : null}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="min-h-0 overflow-hidden rounded-lg border border-neutral-200 bg-white">
          <div className="border-b border-neutral-100 p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-mono text-[11px] uppercase text-neutral-500">{selected.kind}</p>
                <h2 className="mt-1 text-lg font-semibold">{selected.name}</h2>
              </div>
              <button aria-label="Copy trace" className="grid size-8 place-items-center rounded-md border border-neutral-200 hover:bg-neutral-50" type="button">
                <Copy className="size-4" />
              </button>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
              <Metric label="Duration" value={selected.duration} />
              <Metric label="Latency" value={value(row, "duration", "4.93s")} />
              <Metric label="Agent ID" value={value(row, "agent_id", "router-team")} />
              <Metric label="Spans" value={value(row, "spans", "18")} />
            </div>
          </div>

          <div className="border-b border-neutral-100 px-4 py-3">
            <Segmented
              options={[
                ["info", "Info"],
                ["metadata", "Metadata"],
              ]}
              setValue={(next) => setTraceTab(next as TraceTab)}
              value={traceTab}
            />
            <div className="mt-4 rounded-md bg-neutral-50 p-4 font-mono text-xs leading-6 text-neutral-700">
              {traceTab === "info" ? (
                <>
                  <p>span.kind = {selected.kind}</p>
                  <p>span.name = {selected.name}</p>
                  <p>status = {value(row, "status", "OK")}</p>
                </>
              ) : (
                <>
                  <p>trace_id = {traceId}</p>
                  <p>run_id = {value(row, "run_id", "af2bbb00-71ed-452B-aef2-3dfad4930462")}</p>
                  <p>source = mx-agentos-preview</p>
                </>
              )}
            </div>
          </div>

          <TraceTextPanel
            label="Input"
            mode={inputMode}
            onModeChange={setInputMode}
            text={input}
            title="User input"
          />
          <TraceTextPanel
            label="Output"
            mode={outputMode}
            onModeChange={setOutputMode}
            text="Router Team coordinated HR, IT, and finance context and returned the next actionable employee workflow step."
            title="Agent response"
          />
        </section>
      </div>
    </div>
  );
}

function MetaItem({ label, mono = false, value }: { label: string; mono?: boolean; value: string }) {
  return (
    <div className="border-b border-neutral-100 py-3 pr-4 odd:border-r even:pl-4 last:border-b-0">
      <p className="font-mono text-[11px] uppercase text-neutral-500">{label}</p>
      <p className={cn("mt-1 truncate text-sm", mono && "font-mono text-xs")}>{value}</p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="font-mono text-[11px] uppercase text-neutral-500">{label}</p>
      <p className="mt-1 font-mono text-xs">{value}</p>
    </div>
  );
}

function SpanIcon({ kind }: { kind: string }) {
  const className = "size-7 shrink-0 rounded-md p-1.5";
  if (kind === "model") {
    return <MessageSquare className={cn(className, "bg-purple-50 text-purple-600")} />;
  }
  if (kind === "tool") {
    return <Code2 className={cn(className, "bg-sky-50 text-sky-600")} />;
  }
  return <CircleDot className={cn(className, "bg-neutral-950 text-white")} />;
}

function Segmented({
  options,
  setValue,
  value,
}: {
  options: Array<[string, string]>;
  setValue: (value: string) => void;
  value: string;
}) {
  return (
    <div className="inline-flex rounded-md border border-neutral-200 bg-neutral-50 p-0.5">
      {options.map(([key, label]) => (
        <button
          className={cn(
            "h-7 rounded px-3 font-mono text-[11px] uppercase text-neutral-500",
            value === key && "bg-white text-neutral-950 shadow-sm",
          )}
          key={key}
          onClick={() => setValue(key)}
          type="button"
        >
          {label}
        </button>
      ))}
    </div>
  );
}

function TraceTextPanel({
  label,
  mode,
  onModeChange,
  text,
  title,
}: {
  label: string;
  mode: TextMode;
  onModeChange: (mode: TextMode) => void;
  text: string;
  title: string;
}) {
  return (
    <div className="border-b border-neutral-100 p-4 last:border-b-0">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="font-mono text-[11px] uppercase text-neutral-500">{label}</p>
        <Segmented
          options={[
            ["text", "Text"],
            ["formatted", "Formatted"],
          ]}
          setValue={(next) => onModeChange(next as TextMode)}
          value={mode}
        />
      </div>
      <div className="rounded-md bg-neutral-50 p-4">
        {mode === "formatted" ? (
          <>
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className="mt-3 text-sm leading-6 text-neutral-700">{text}</p>
          </>
        ) : (
          <pre className="whitespace-pre-wrap font-mono text-xs leading-6 text-neutral-700">{text}</pre>
        )}
      </div>
    </div>
  );
}

function TracesEmptyOverlay() {
  return (
    <div className="absolute inset-0 grid place-items-center bg-white/60 backdrop-blur-[2px]">
      <div className="max-w-md text-center">
        <div className="mb-6 inline-flex items-center gap-2">
          <span className="grid size-10 place-items-center rounded-full bg-neutral-950 text-white">
            <PanelRightOpen className="size-5" />
          </span>
          <span className="grid size-10 place-items-center rounded-full bg-[#ff3b25] text-white">
            <AlertTriangle className="size-5" />
          </span>
        </div>
        <h2 className="text-2xl font-semibold">No traces logged</h2>
        <p className="mt-2 text-sm leading-6 text-neutral-600">
          View traces created by agents and teams. Visit docs for more information.
        </p>
        <div className="mt-6 flex justify-center gap-2">
          <CommandButton>
            Learn more
            <ExternalLink className="size-3.5" />
          </CommandButton>
          <CommandButton className="border-neutral-950 bg-neutral-950 text-white hover:bg-neutral-800">
            Go to chat page
          </CommandButton>
        </div>
      </div>
    </div>
  );
}
