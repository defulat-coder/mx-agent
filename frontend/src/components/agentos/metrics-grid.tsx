import type { MetricsResponse } from "@/lib/agentos-types";

export function MetricsGrid({ data }: { data: MetricsResponse }) {
  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-auto px-5 py-5">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="text-xs text-neutral-500">Period</p>
          <h1 className="font-mono text-sm">{data.period}</h1>
        </div>
        <button className="rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2 font-mono text-[11px] uppercase">
          Last 30 days
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {data.metrics.map((metric) => {
          const max = Math.max(...metric.points.map((point) => point.value), 1);

          return (
            <section className="rounded-lg border border-neutral-200 bg-white p-4" key={metric.label}>
              <p className="font-mono text-[11px] uppercase text-neutral-500">{metric.label}</p>
              <p className="mt-2 text-3xl font-semibold">{metric.value}</p>
              <div className="mt-6 flex h-24 items-end gap-2">
                {metric.points.map((point) => (
                  <div className="flex flex-1 flex-col items-center gap-2" key={point.label}>
                    <span
                      className="w-full rounded-t bg-neutral-900"
                      style={{ height: `${Math.max(8, (point.value / max) * 88)}px` }}
                    />
                    <span className="font-mono text-[10px] text-neutral-400">{point.label}</span>
                  </div>
                ))}
              </div>
            </section>
          );
        })}
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[2fr_1fr]">
        <section className="rounded-lg border border-neutral-200 bg-white p-4">
          <h2 className="text-sm font-semibold">Model Runs</h2>
          <div className="mt-4 space-y-3">
            {data.model_runs.map((run) => (
              <div className="flex items-center justify-between border-b border-neutral-100 pb-3" key={String(run.model)}>
                <span className="font-mono text-xs">{String(run.model)}</span>
                <span className="text-sm text-neutral-500">{String(run.share)}</span>
              </div>
            ))}
          </div>
        </section>
        <section className="rounded-lg border border-neutral-200 bg-neutral-50 p-4">
          <h2 className="text-sm font-semibold">Analytics</h2>
          <p className="mt-3 text-sm leading-6 text-neutral-500">{data.gated_message}</p>
        </section>
      </div>
    </div>
  );
}
