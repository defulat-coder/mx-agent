"use client";

import { ChevronLeft, ChevronRight, Download, ExternalLink } from "lucide-react";
import { useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { MetricsResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type MetricSeries = MetricsResponse["metrics"][number];

const months = ["APR 2026", "MAY 2026", "JUN 2026"];

function formatAxis(max: number) {
  if (max >= 1000) {
    const step = Math.ceil(max / 4000) * 1000;
    return [0, step, step * 2, step * 3, step * 4].map((value) => (value === 0 ? "0" : `${value / 1000}K`));
  }
  const step = Math.max(1, Math.ceil(max / 4));
  return [0, step, step * 2, step * 3, step * 4].map(String);
}

function linePath(series: MetricSeries) {
  const max = Math.max(...series.points.map((point) => point.value), 1);
  return series.points
    .map((point, index) => {
      const x = 36 + (index / Math.max(series.points.length - 1, 1)) * 384;
      const y = 168 - (point.value / max) * 136;
      return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function MetricChart({
  selected,
  series,
  onSelect,
}: {
  selected: boolean;
  series: MetricSeries;
  onSelect: () => void;
}) {
  const max = Math.max(...series.points.map((point) => point.value), 1);
  const axis = formatAxis(max);

  return (
    <button
      className={cn(
        "group min-h-[260px] rounded-md border border-transparent bg-white p-4 text-left transition-colors hover:border-neutral-200",
        selected && "border-neutral-300 bg-neutral-50",
      )}
      onClick={onSelect}
      type="button"
    >
      <div className="mb-3 flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-neutral-700">{series.label}</p>
          <p className="mt-1 text-3xl font-semibold">{series.value}</p>
        </div>
        <span className="grid size-7 place-items-center rounded-md text-neutral-400 group-hover:bg-neutral-100 group-hover:text-neutral-800">
          <Download className="size-3.5" />
        </span>
      </div>
      <svg aria-label={`${series.label} chart`} className="h-[180px] w-full" role="img" viewBox="0 0 440 180">
        <defs>
          <pattern height="12" id={`metrics-dot-${series.label.replace(/\s+/g, "-")}`} patternUnits="userSpaceOnUse" width="12">
            <circle cx="1" cy="1" fill="#e5e5e5" r="0.8" />
          </pattern>
        </defs>
        <rect fill={`url(#metrics-dot-${series.label.replace(/\s+/g, "-")})`} height="144" width="392" x="36" y="24" />
        {axis.map((label, index) => {
          const y = 168 - index * 34;
          return (
            <g key={label}>
              <text fill="#a3a3a3" fontSize="10" x="8" y={y + 3}>
                {label}
              </text>
              <line stroke="#f1f1f1" strokeWidth="1" x1="36" x2="428" y1={y} y2={y} />
            </g>
          );
        })}
        {[1, 8, 15, 22, 29].map((day) => {
          const x = 36 + ((day - 1) / 28) * 384;
          return (
            <text fill="#a3a3a3" fontSize="10" key={day} textAnchor="middle" x={x} y="178">
              {day}
            </text>
          );
        })}
        <path d={linePath(series)} fill="none" stroke="#202020" strokeLinejoin="round" strokeWidth="1.35" />
      </svg>
    </button>
  );
}

export function MetricsGrid({ data }: { data: MetricsResponse }) {
  const [monthIndex, setMonthIndex] = useState(months.indexOf(data.period) >= 0 ? months.indexOf(data.period) : 2);
  const [exported, setExported] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState(data.metrics[0]?.label ?? "");

  const selected = useMemo(
    () => data.metrics.find((metric) => metric.label === selectedMetric) ?? data.metrics[0],
    [data.metrics, selectedMetric],
  );

  const totalModelRuns = data.model_runs.reduce((sum, run) => sum + Number(run.runs ?? 0), 0);

  return (
    <div className="min-h-0 flex-1 overflow-auto px-5 py-5">
      <div className="mb-8 flex items-start justify-between gap-4">
        <div className="flex gap-6 text-sm">
          <div>
            <p className="mb-1 text-xs text-neutral-500">Database</p>
            <p className="whitespace-nowrap font-medium">{data.database}</p>
          </div>
          <div className="pt-6 font-mono text-neutral-500">/</div>
          <div>
            <p className="mb-1 text-xs text-neutral-500">Table</p>
            <p className="whitespace-nowrap font-medium">{data.table}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
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
          <div className="inline-flex h-9 items-center gap-1 rounded-md border border-neutral-200 bg-neutral-50 px-2 font-mono text-[11px] uppercase">
            <button
              aria-label="Select previous month"
              className="grid size-6 place-items-center rounded text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900"
              onClick={() => setMonthIndex((index) => Math.max(0, index - 1))}
              type="button"
            >
              <ChevronLeft className="size-3.5" />
            </button>
            <span className="min-w-20 text-center">{months[monthIndex]}</span>
            <button
              aria-label="Select next month"
              className="grid size-6 place-items-center rounded text-neutral-500 enabled:hover:bg-neutral-100 enabled:hover:text-neutral-900 disabled:opacity-35"
              disabled={monthIndex === months.length - 1}
              onClick={() => setMonthIndex((index) => Math.min(months.length - 1, index + 1))}
              type="button"
            >
              <ChevronRight className="size-3.5" />
            </button>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        {data.metrics.map((metric) => (
          <MetricChart
            key={metric.label}
            onSelect={() => setSelectedMetric(metric.label)}
            selected={selected?.label === metric.label}
            series={metric}
          />
        ))}
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1.2fr_1fr]">
        <section className="rounded-md border border-neutral-200 bg-white p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold">Model runs</h2>
              <p className="mt-1 text-3xl font-semibold">{totalModelRuns || 688}</p>
            </div>
            <p className="font-mono text-[11px] uppercase text-neutral-500">Selected: {selected?.label}</p>
          </div>
          <div className="space-y-3">
            {data.model_runs.map((run) => {
              const share = Number(String(run.share ?? "0").replace("%", ""));
              return (
                <div className="grid grid-cols-[96px_1fr_48px] items-center gap-3" key={String(run.model)}>
                  <button className="truncate text-left font-mono text-xs" type="button">
                    {String(run.model)}
                  </button>
                  <div className="h-2 rounded-full bg-neutral-100">
                    <div className="h-2 rounded-full bg-neutral-900" style={{ width: `${Math.max(4, share)}%` }} />
                  </div>
                  <span className="text-right text-sm text-neutral-500">{String(run.share)}</span>
                </div>
              );
            })}
          </div>
        </section>

        <section className="relative min-h-[220px] overflow-hidden rounded-md border border-neutral-200 bg-white p-6">
          <div className="absolute inset-x-8 bottom-8 top-20 opacity-20 blur-[2px]">
            <div className="flex h-full items-end gap-2">
              {Array.from({ length: 28 }).map((_, index) => (
                <span
                  className="flex-1 rounded-t bg-neutral-300"
                  key={index}
                  style={{ height: `${24 + ((index * 17) % 74)}%` }}
                />
              ))}
            </div>
          </div>
          <div className="relative z-10 grid h-full place-items-center text-center">
            <div>
              <h2 className="text-2xl font-semibold">Not available for Demo OS</h2>
              <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-neutral-500">{data.gated_message}</p>
              <CommandButton className="mt-5">
                <ExternalLink className="size-3.5" />
                Learn More
              </CommandButton>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
