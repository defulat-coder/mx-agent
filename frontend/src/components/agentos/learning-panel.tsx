"use client";

import { AlertTriangle, CircleOff } from "lucide-react";

export const learningSections = [
  { id: "user_memory", label: "User Memories" },
  { id: "user_profile", label: "User Profiles" },
  { id: "entity_memory", label: "Entity Memories" },
  { id: "session_context", label: "Session Context" },
  { id: "decision_log", label: "Decision Logs" },
] as const;

export type LearningSectionId = (typeof learningSections)[number]["id"];

const entityRows = [
  ["Acme Corp", "ORGANIZATION", "15 Jan 2025, 14:16"],
  ["Sarah Chen", "PERSON", "14 Jan 2025, 10:30"],
  ["Project Phoenix", "PROJECT", "13 Jan 2025, 16:45"],
  ["Q3 Roadmap", "DOCUMENT", "12 Jan 2025, 09:12"],
  ["Stripe", "INTEGRATION", "11 Jan 2025, 18:22"],
  ["Marcus Lee", "PERSON", "10 Jan 2025, 11:05"],
  ["Design System", "PROJECT", "9 Jan 2025, 15:48"],
  ["Series A Round", "EVENT", "8 Jan 2025, 08:27"],
  ["Kubernetes Migration", "PROJECT", "7 Jan 2025, 13:19"],
  ["Postgres Cluster", "INFRASTRUCTURE", "6 Jan 2025, 17:42"],
] as const;

export function LearningPanel({ section }: { section: LearningSectionId }) {
  if (section === "user_memory") {
    return <LearningLoading section={section} />;
  }

  return (
    <div className="relative min-h-0 flex-1 overflow-hidden bg-white">
      <div className="absolute inset-x-4 top-4 bottom-10 overflow-hidden rounded-lg border border-neutral-100 bg-white">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="h-12 border-b border-neutral-100 text-left font-mono text-[11px] uppercase text-neutral-500">
              <th className="w-12 px-4 font-normal" />
              <th className="font-normal">Entity Name</th>
              <th className="w-80 font-normal">Entity Type</th>
              <th className="w-64 pr-4 text-right font-normal">Updated At</th>
            </tr>
          </thead>
          <tbody>
            {entityRows.map(([name, type, updatedAt]) => (
              <tr className="h-14 border-b border-neutral-100 text-neutral-700" key={name}>
                <td className="px-4">
                  <span className="block size-4 rounded border border-neutral-300 bg-white" />
                </td>
                <td className="font-medium text-neutral-700">{name}</td>
                <td>
                  <span className="rounded bg-neutral-50 px-2 py-1 font-mono text-[11px] text-neutral-600">
                    {type}
                  </span>
                </td>
                <td className="pr-4 text-right text-neutral-400">{updatedAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="absolute inset-0 bg-white/60 backdrop-blur-[2.5px]" />

      <div className="absolute left-1/2 top-[45%] w-[380px] -translate-x-1/2 -translate-y-1/2 text-center">
        <div className="mb-8 flex justify-center -space-x-2">
          <span className="grid size-6 place-items-center rounded-full bg-neutral-950 text-white">
            <CircleOff className="size-3.5" />
          </span>
          <span className="grid size-6 rotate-12 place-items-center rounded-full bg-[#ff3b25] text-white">
            <AlertTriangle className="size-3.5" />
          </span>
        </div>
        <h2 className="text-3xl font-semibold tracking-normal">AgentOS not active</h2>
        <p className="mx-auto mt-3 max-w-80 text-sm leading-6 text-neutral-500">
          Your AgentOS is connected but is not active. After running the AgentOS you need to refresh the page.
        </p>
        <div className="mt-7 grid grid-cols-2 gap-2">
          <button
            className="h-10 rounded-lg bg-neutral-100 font-mono text-[11px] uppercase text-neutral-700"
            type="button"
          >
            Learn More
          </button>
          <button className="h-10 rounded-lg bg-neutral-950 font-mono text-[11px] uppercase text-white" type="button">
            Refresh
          </button>
        </div>
        <div className="my-5 flex items-center gap-3 text-xs text-neutral-400">
          <span className="h-px flex-1 bg-neutral-200" />
          OR
          <span className="h-px flex-1 bg-neutral-200" />
        </div>
        <button className="h-10 w-full rounded-lg bg-neutral-100 font-mono text-[11px] uppercase text-neutral-700" type="button">
          Explore a Live Demo AgentOS
        </button>
      </div>

      <div className="absolute bottom-5 right-5 flex h-14 w-[360px] items-center gap-3 rounded-lg border border-neutral-200 bg-white px-4 text-sm text-neutral-700 shadow-sm">
        <span className="h-7 w-1 rounded-full bg-[#ff3b25]" />
        Failed to connect to the AgentOS
      </div>
    </div>
  );
}

function LearningLoading({ section }: { section: LearningSectionId }) {
  return (
    <div className="grid min-h-0 flex-1 place-items-center">
      <div className="flex items-center gap-1.5" aria-label={`${section} loading`}>
        <span className="size-2 rounded-full bg-neutral-300" />
        <span className="size-2 rounded-full bg-neutral-300" />
        <span className="size-2 rounded-full bg-neutral-300" />
      </div>
    </div>
  );
}
