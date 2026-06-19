import { ExternalLink, MessageSquare, Play, Server } from "lucide-react";
import Link from "next/link";

import { CommandButton } from "@/components/agentos/command-button";

const icons = {
  sessions: Play,
  traces: Server,
  chat: MessageSquare,
};

export function StatusState({
  title,
  description,
  actionHref,
  actionLabel,
  icon = "sessions",
}: {
  title: string;
  description: string;
  actionHref?: string;
  actionLabel?: string;
  icon?: keyof typeof icons;
}) {
  const Icon = icons[icon];

  return (
    <div className="pointer-events-none absolute inset-x-0 top-36 z-10 flex justify-center">
      <div className="pointer-events-auto flex w-full max-w-xl flex-col items-center text-center">
        <div className="mb-8 flex -space-x-2">
          <span className="grid size-9 rotate-[-14deg] place-items-center rounded-xl border border-neutral-200 bg-white shadow-sm">
            <Icon className="size-5" />
          </span>
          <span className="grid size-9 rotate-[14deg] place-items-center rounded-xl border border-red-100 bg-white text-[#ff3b25] shadow-sm">
            <Server className="size-5" />
          </span>
        </div>
        <h2 className="text-3xl font-semibold tracking-normal">{title}</h2>
        <p className="mt-3 max-w-md text-sm leading-6 text-neutral-500">{description}</p>
        <div className="mt-6 flex items-center gap-3">
          <CommandButton>
            Learn More
            <ExternalLink className="size-3" />
          </CommandButton>
          {actionHref && actionLabel ? (
            <Link
              className="inline-flex h-9 items-center rounded-md bg-neutral-950 px-4 font-mono text-[11px] uppercase text-white hover:bg-neutral-800"
              href={actionHref}
            >
              {actionLabel}
            </Link>
          ) : null}
        </div>
      </div>
    </div>
  );
}
