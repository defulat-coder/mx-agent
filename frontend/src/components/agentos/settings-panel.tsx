import { SettingsNav } from "@/components/agentos/settings-nav";
import type { SettingsResponse } from "@/lib/agentos-types";

export function SettingsPanel({
  active,
  settings,
}: {
  active: keyof SettingsResponse | "roles";
  settings: SettingsResponse;
}) {
  const data = active === "roles" ? { owner: "MX Operator", role: "Owner", status: "Active" } : settings[active];

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-auto px-5 py-5">
      <div className="mb-6">
        <p className="font-mono text-[11px] uppercase text-neutral-500">Settings</p>
        <h1 className="mt-1 text-2xl font-semibold capitalize">{active}</h1>
      </div>
      <SettingsNav />
      <section className="max-w-3xl rounded-lg border border-neutral-200 bg-white">
        {Object.entries(data).map(([key, value]) => (
          <div className="grid grid-cols-[180px_1fr] border-b border-neutral-100 px-4 py-4 last:border-0" key={key}>
            <span className="font-mono text-[11px] uppercase text-neutral-500">{key.replaceAll("_", " ")}</span>
            <span className="text-sm text-neutral-800">
              {Array.isArray(value) ? value.join(", ") : typeof value === "object" ? JSON.stringify(value) : String(value)}
            </span>
          </div>
        ))}
      </section>
    </div>
  );
}
