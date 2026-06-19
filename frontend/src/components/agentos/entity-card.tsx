import { Bot, GitBranch, Pencil, Server, Trash2 } from "lucide-react";
import Link from "next/link";

import { CommandButton } from "@/components/agentos/command-button";
import type { EntityCardData } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

const iconByKind = {
  agent: Bot,
  team: Bot,
  workflow: GitBranch,
  interface: Server,
  os: Server,
};

export function EntityCard({ entity }: { entity: EntityCardData }) {
  const Icon = iconByKind[entity.kind];

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
          {entity.tags.map((tag) => (
            <span
              className="rounded-md bg-neutral-100 px-2 py-1 font-mono text-[11px] uppercase text-neutral-900"
              key={tag}
            >
              {tag}
            </span>
          ))}
          {entity.stats.map((stat) => (
            <span
              className="rounded-md bg-neutral-100 px-2 py-1 font-mono text-[11px] uppercase text-neutral-900"
              key={stat}
            >
              {stat}
            </span>
          ))}
        </div>
      </div>
      <div className="flex gap-2 border-t border-neutral-200 bg-neutral-50 px-3 py-2">
        {entity.actions.includes("chat") ? (
          <Link
            className={cn(
              "inline-flex h-6 items-center justify-center rounded-md border border-neutral-200 bg-neutral-50 px-2 font-mono text-[11px] uppercase text-neutral-900 hover:bg-neutral-100",
            )}
            href="/chat"
          >
            Chat
          </Link>
        ) : null}
        {entity.actions.includes("config") ? <CommandButton className="h-6 px-2">Config</CommandButton> : null}
        {entity.actions.includes("edit") ? (
          <CommandButton className="h-6 px-2">
            <Pencil className="size-3" />
            Edit
          </CommandButton>
        ) : null}
        {entity.actions.includes("delete") ? (
          <CommandButton className="h-6 px-2">
            <Trash2 className="size-3" />
            Delete
          </CommandButton>
        ) : null}
      </div>
    </article>
  );
}
