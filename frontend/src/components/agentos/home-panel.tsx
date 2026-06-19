"use client";

import { Bot, ChevronUp, GitBranch, Server } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import type { EntityCardData, EntityKind } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type SectionKey = "agents" | "teams" | "workflows";

type HomeSections = Record<SectionKey, EntityCardData[]>;

const labels: Record<SectionKey, string> = {
  agents: "Agents",
  teams: "Teams",
  workflows: "Workflows",
};

const iconByKind: Record<EntityKind, typeof Bot> = {
  agent: Bot,
  team: Bot,
  workflow: GitBranch,
  interface: Server,
  os: Server,
};

function configHref(entity: EntityCardData) {
  return `/config?type=${entity.kind}&id=${entity.id}`;
}

function chatHref(entity: EntityCardData) {
  return `/chat?type=${entity.kind}&id=${entity.id}`;
}

export function HomePanel({ sections }: { sections: HomeSections }) {
  const [collapsed, setCollapsed] = useState<Record<SectionKey, boolean>>({
    agents: false,
    teams: false,
    workflows: false,
  });
  const [expanded, setExpanded] = useState<Record<SectionKey, boolean>>({
    agents: false,
    teams: false,
    workflows: false,
  });

  const toggleCollapsed = (key: SectionKey) => {
    setCollapsed((current) => ({ ...current, [key]: !current[key] }));
  };

  const toggleExpanded = (key: SectionKey) => {
    setExpanded((current) => ({ ...current, [key]: !current[key] }));
  };

  return (
    <div className="agno-scrollbar min-h-0 flex-1 overflow-auto px-5 py-6">
      {(Object.keys(labels) as SectionKey[]).map((key) => {
        const entities = sections[key];
        const visible = expanded[key] ? entities : entities.slice(0, 3);
        const hiddenCount = Math.max(entities.length - 3, 0);

        return (
          <section className="mb-8" key={key}>
            <button
              className="mb-6 flex items-center gap-2 rounded-md pr-2 text-left hover:bg-neutral-50"
              onClick={() => toggleCollapsed(key)}
              type="button"
            >
              <ChevronUp className={cn("size-4 transition-transform", collapsed[key] && "rotate-180")} />
              <h2 className="font-mono text-[12px] uppercase">{labels[key]}</h2>
            </button>

            {collapsed[key] ? null : (
              <>
                <div className="grid gap-4 xl:grid-cols-3">
                  {visible.map((entity) => (
                    <HomeEntityCard entity={entity} key={entity.id} />
                  ))}
                </div>
                {hiddenCount ? (
                  <button
                    className="mt-4 rounded-md bg-neutral-100 px-3 py-2 font-mono text-[11px] uppercase hover:bg-neutral-200"
                    onClick={() => toggleExpanded(key)}
                    type="button"
                  >
                    {expanded[key] ? "Show Less" : `Show More (+${hiddenCount})`}
                  </button>
                ) : null}
              </>
            )}
          </section>
        );
      })}
    </div>
  );
}

function HomeEntityCard({ entity }: { entity: EntityCardData }) {
  const Icon = iconByKind[entity.kind] ?? Bot;
  const primaryTags = entity.tags.slice(0, 3);
  const overflow = Math.max(entity.tags.length - primaryTags.length, 0);

  return (
    <article className="flex min-h-40 flex-col overflow-hidden rounded-lg border border-neutral-200 bg-white">
      <div className="flex-1 p-3">
        <div className="mb-3 flex items-center gap-2">
          <span className="grid size-6 place-items-center rounded-md bg-[#ff3b25] text-white">
            <Icon className="size-3.5" />
          </span>
          <h3 className="text-sm font-semibold">{entity.name}</h3>
        </div>
        <p className="line-clamp-2 text-sm leading-6 text-neutral-600">{entity.description}</p>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {primaryTags.map((tag) => (
            <span className="rounded-md bg-neutral-100 px-2 py-1 font-mono text-[11px] uppercase text-neutral-900" key={tag}>
              {tag}
            </span>
          ))}
          {overflow ? (
            <span className="rounded-md bg-neutral-100 px-2 py-1 font-mono text-[11px] uppercase text-neutral-900">
              +{overflow}
            </span>
          ) : null}
        </div>
      </div>
      <div className="flex gap-2 border-t border-neutral-200 bg-neutral-50 px-3 py-2">
        <Link
          className="inline-flex h-6 items-center justify-center rounded-md border border-neutral-200 bg-neutral-50 px-2 font-mono text-[11px] uppercase text-neutral-900 hover:bg-neutral-100"
          href={chatHref(entity)}
        >
          Chat
        </Link>
        <Link
          className="inline-flex h-6 items-center justify-center rounded-md border border-neutral-200 bg-neutral-50 px-2 font-mono text-[11px] uppercase text-neutral-900 hover:bg-neutral-100"
          href={configHref(entity)}
        >
          Config
        </Link>
      </div>
    </article>
  );
}
