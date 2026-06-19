"use client";

import { Bot, ChevronDown, ExternalLink, MessageSquare, PanelLeft } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import type { EntityCardData, EntityKind } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

const docsUrl = "https://docs.agno.com/reference/agents/agent";

const configSections = [
  "Agent Details",
  "Model",
  "Database",
  "Tools",
  "Sessions",
  "Default Tools",
  "System Message",
] as const;

function sectionRows(section: string, entity: EntityCardData) {
  const baseRows: Record<string, Array<[string, string]>> = {
    "Agent Details": [
      ["Agent Id", entity.id],
      ["Agent Name", entity.name],
      ["Kind", entity.kind],
    ],
    Model: [["Model", entity.kind === "workflow" ? "gpt-5.5-mini" : "gpt-5.5"]],
    Database: [["Storage", "mx-agent-db"]],
    Tools: [
      ["Configured", String(Math.max(entity.tags.length, 1))],
      ["Tags", entity.tags.join(", ") || "none"],
    ],
    Sessions: [["Default", "enabled"]],
    "Default Tools": [["Memory", entity.kind === "agent" ? "enabled" : "inherited"]],
    "System Message": [["Scope", entity.description]],
  };
  return baseRows[section] ?? [];
}

function kindLabel(kind: EntityKind) {
  if (kind === "agent") return "agent";
  if (kind === "team") return "team";
  if (kind === "workflow") return "workflow";
  return kind;
}

export function ConfigPanel({ entity }: { entity: EntityCardData }) {
  const [openSections, setOpenSections] = useState<string[]>(["Agent Details"]);

  const toggle = (section: string) => {
    setOpenSections((current) =>
      current.includes(section) ? current.filter((item) => item !== section) : [...current, section],
    );
  };

  return (
    <div className="flex min-h-0 flex-1">
      <div className="flex min-w-0 flex-1 flex-col px-5 py-5">
        <div className="mb-5 flex items-center gap-2 text-sm">
          <Link className="font-mono text-[11px] uppercase text-neutral-500 hover:text-neutral-900" href="/">
            Home
          </Link>
          <span className="text-neutral-300">/</span>
          <span>{entity.name}</span>
        </div>

        <div className="mb-5 flex items-center gap-3">
          <span className="grid size-8 place-items-center rounded-md bg-[#ff3b25] text-white">
            <Bot className="size-4" />
          </span>
          <div>
            <p className="font-mono text-[11px] uppercase text-neutral-500">{kindLabel(entity.kind)}</p>
            <h1 className="text-2xl font-semibold">{entity.name}</h1>
          </div>
        </div>

        <div className="flex gap-2">
          <Link
            className="inline-flex h-9 items-center justify-center gap-1.5 rounded-md border border-neutral-200 bg-neutral-50 px-4 font-mono text-[11px] uppercase text-neutral-900 transition-colors hover:bg-neutral-100"
            href={`/chat?type=${kindLabel(entity.kind)}&id=${entity.id}`}
          >
            <MessageSquare className="size-3.5" />
            Open in chat
          </Link>
          <a
            className="inline-flex h-9 items-center justify-center gap-1.5 rounded-md border border-neutral-200 bg-neutral-50 px-4 font-mono text-[11px] uppercase text-neutral-900 transition-colors hover:bg-neutral-100"
            href={docsUrl}
          >
            <ExternalLink className="size-3.5" />
            Open docs
          </a>
        </div>
      </div>

      <aside className="w-[480px] shrink-0 border-l border-neutral-200 bg-white">
        <div className="flex h-14 items-center justify-between border-b border-neutral-100 px-4">
          <div>
            <p className="font-mono text-[11px] uppercase text-neutral-500">{entity.name}</p>
            <h2 className="text-sm font-semibold">Configuration</h2>
          </div>
          <Link
            aria-label="Back home"
            className="grid size-8 place-items-center rounded-md text-neutral-500 hover:bg-neutral-100"
            href="/"
          >
            <PanelLeft className="size-4" />
          </Link>
        </div>

        <div className="agno-scrollbar h-[calc(100%-56px)] overflow-auto p-4">
          {configSections.map((section) => {
            const open = openSections.includes(section);
            const rows = sectionRows(section, entity);
            const badge = section === "Tools" ? String(Math.max(entity.tags.length, 1)) : section === "Default Tools" ? "1" : null;

            return (
              <div className="border-b border-neutral-100 py-2" key={section}>
                <button
                  className="flex w-full items-center justify-between rounded-md px-2 py-2 text-left hover:bg-neutral-50"
                  onClick={() => toggle(section)}
                  type="button"
                >
                  <span className="flex items-center gap-2 text-sm font-medium">
                    {section}
                    {badge ? (
                      <span className="rounded bg-neutral-100 px-1.5 py-0.5 font-mono text-[10px] text-neutral-600">
                        {badge}
                      </span>
                    ) : null}
                  </span>
                  <ChevronDown className={cn("size-4 transition-transform", open && "rotate-180")} />
                </button>
                {open ? (
                  <div className="px-2 pb-3">
                    {rows.map(([label, value]) => (
                      <div className="grid grid-cols-[120px_1fr] gap-3 border-t border-neutral-100 py-2" key={label}>
                        <span className="font-mono text-[11px] uppercase text-neutral-500">{label}</span>
                        <span className="min-w-0 break-words text-sm text-neutral-900">{value}</span>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            );
          })}
        </div>
      </aside>
    </div>
  );
}

export function MissingConfigPanel() {
  return (
    <div className="grid min-h-0 flex-1 place-items-center">
      <div className="text-center">
        <p className="text-xl font-semibold">Configuration not found</p>
        <Link
          className="mt-4 inline-flex h-9 items-center justify-center rounded-md border border-neutral-200 bg-neutral-50 px-4 font-mono text-[11px] uppercase text-neutral-900 hover:bg-neutral-100"
          href="/"
        >
          Back Home
        </Link>
      </div>
    </div>
  );
}
