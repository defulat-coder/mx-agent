"use client";

import { Bot, ChevronDown, Database, MessageSquare, Pencil, Plus, RotateCcw, Save } from "lucide-react";
import { useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { EntityCardData } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type StudioMode = "list" | "builder";

const models = [
  "claude-haiku-4-5-20251001 (Anthropic)",
  "claude-opus-4-6 (Anthropic)",
  "claude-sonnet-4-6 (Anthropic)",
  "gemini-3-flash-preview (Google)",
  "gpt-5.5 (OpenAI)",
];

const sections = [
  ["Basics", "Configure the core identity and behaviour of your agent"],
  ["Context Management", "Control the information sent to language models"],
  ["Session State", "Session state configuration"],
  ["Knowledge", "Knowledge base configuration for retrieval"],
  ["Memory", "Long-term user memory management"],
  ["Advanced", "Additional configuration as JSON"],
] as const;

export function StudioPanel({ agents }: { agents: EntityCardData[] }) {
  const [mode, setMode] = useState<StudioMode>("list");
  const [editingAgent, setEditingAgent] = useState<EntityCardData | null>(null);

  const openBuilder = (agent: EntityCardData | null) => {
    setEditingAgent(agent);
    setMode("builder");
  };

  if (mode === "builder") {
    return <AgentBuilder agent={editingAgent} onBack={() => setMode("list")} />;
  }

  return (
    <div className="agno-scrollbar min-h-0 flex-1 overflow-auto px-5 py-5">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="font-mono text-[12px] uppercase">{agents.length} Agents</h1>
        <CommandButton className="h-9 px-4" onClick={() => openBuilder(null)} tone="dark">
          <Plus className="size-3.5" />
          New Agent
        </CommandButton>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        {agents.map((agent) => (
          <article className="flex min-h-40 flex-col overflow-hidden rounded-lg border border-neutral-200 bg-white" key={agent.id}>
            <div className="flex-1 p-3">
              <div className="mb-3 flex items-center gap-2">
                <span className="grid size-6 place-items-center rounded-md bg-[#ff3b25] text-white">
                  <Bot className="size-3.5" />
                </span>
                <h2 className="text-sm font-semibold">{agent.name}</h2>
              </div>
              <p className="line-clamp-2 text-sm leading-6 text-neutral-600">{agent.description}</p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                <span className="rounded-md bg-neutral-100 px-2 py-1 font-mono text-[11px] uppercase text-neutral-900">
                  Current Version 1
                </span>
                {agent.tags.slice(0, 2).map((tag) => (
                  <span className="rounded-md bg-neutral-100 px-2 py-1 font-mono text-[11px] uppercase text-neutral-900" key={tag}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            <div className="flex gap-2 border-t border-neutral-200 bg-neutral-50 px-3 py-2">
              <CommandButton className="h-6 px-2">
                <MessageSquare className="size-3" />
                Chat
              </CommandButton>
              <CommandButton className="h-6 px-2" onClick={() => openBuilder(agent)}>
                <Pencil className="size-3" />
                Edit
              </CommandButton>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

function AgentBuilder({ agent, onBack }: { agent: EntityCardData | null; onBack: () => void }) {
  const [name, setName] = useState(agent?.name ?? "");
  const [model, setModel] = useState(models[0]);
  const [instructions, setInstructions] = useState(agent?.description ?? "");
  const [activeSection, setActiveSection] = useState("Basics");
  const [draftSaved, setDraftSaved] = useState(false);

  const publishEnabled = name.trim().length > 0;
  const preview = useMemo(
    () => [
      ["Name", name.trim() || "No name given yet"],
      ["Model", model || "No model given yet"],
      ["Instructions", instructions.trim() || "No instructions given yet"],
      ["Tools", "No tools given yet"],
      ["Database", "mx-agent-db"],
    ],
    [instructions, model, name],
  );

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="border-b border-neutral-100 px-5 py-5">
        <button className="mb-4 font-mono text-[11px] uppercase text-neutral-500 hover:text-neutral-900" onClick={onBack} type="button">
          Agents
        </button>
        <h1 className="text-2xl font-semibold">{agent ? agent.name : "New Agent"}</h1>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_420px]">
        <div className="agno-scrollbar min-h-0 overflow-auto px-5 py-5">
          <section className="mb-5 rounded-lg border border-neutral-200 bg-white">
            <button
              className="flex w-full items-center justify-between px-4 py-4 text-left"
              onClick={() => setActiveSection("Basics")}
              type="button"
            >
              <span>
                <span className="block text-sm font-semibold">Basics</span>
                <span className="mt-1 block text-xs text-neutral-500">Configure the core identity and behaviour of your agent</span>
              </span>
              <ChevronDown className="size-4" />
            </button>

            <div className="space-y-5 border-t border-neutral-100 px-4 py-5">
              <label className="block">
                <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Agent Name</span>
                <input
                  className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none placeholder:text-neutral-400 focus:border-neutral-400"
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Enter agent name"
                  value={name}
                />
              </label>

              <label className="block">
                <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Model</span>
                <select
                  className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-neutral-400"
                  onChange={(event) => setModel(event.target.value)}
                  value={model}
                >
                  {models.map((option) => (
                    <option key={option}>{option}</option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Instructions Optional</span>
                <textarea
                  className="min-h-24 w-full resize-none rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none placeholder:text-neutral-400 focus:border-neutral-400"
                  onChange={(event) => setInstructions(event.target.value)}
                  placeholder="Enter instructions"
                  value={instructions}
                />
              </label>

              <div>
                <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Tools Optional</span>
                <button
                  className="flex h-9 w-full items-center justify-between rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-600"
                  type="button"
                >
                  <span>Select tools</span>
                  <span className="font-mono text-[11px] uppercase">No tools selected</span>
                </button>
              </div>

              <label className="block">
                <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Database Optional</span>
                <select
                  className="h-9 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm text-neutral-500 outline-none"
                  disabled
                  value="mx-agent-db"
                >
                  <option>mx-agent-db</option>
                </select>
                <span className="mt-2 block text-xs text-neutral-500">In demo mode, the database is auto-selected.</span>
              </label>
            </div>
          </section>

          <div className="space-y-2">
            {sections.slice(1).map(([title, description]) => (
              <button
                className={cn(
                  "flex w-full items-center justify-between rounded-lg border border-neutral-200 px-4 py-4 text-left hover:bg-neutral-50",
                  activeSection === title && "bg-neutral-50",
                )}
                key={title}
                onClick={() => setActiveSection(title)}
                type="button"
              >
                <span>
                  <span className="block text-sm font-semibold">{title}</span>
                  <span className="mt-1 block text-xs text-neutral-500">{description}</span>
                </span>
                <ChevronDown className="size-4" />
              </button>
            ))}
          </div>
        </div>

        <aside className="flex min-h-0 flex-col border-l border-neutral-200 bg-white">
          <div className="border-b border-neutral-100 px-4 py-5">
            <p className="font-mono text-[11px] uppercase text-neutral-500">Name of agent</p>
            <h2 className="mt-1 text-sm font-semibold">{activeSection}</h2>
          </div>
          <div className="min-h-0 flex-1 overflow-auto px-4 py-4">
            <div className="rounded-lg bg-neutral-50 p-4">
              <p className="mb-3 font-mono text-[11px] uppercase text-neutral-500">Basics</p>
              {preview.map(([label, value]) => (
                <div className="border-b border-neutral-200/70 py-3 last:border-b-0" key={label}>
                  <p className="font-mono text-[11px] uppercase text-neutral-500">{label}</p>
                  <p className="mt-1 break-words text-sm text-neutral-900">{value}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2 border-t border-neutral-100 p-4">
            <CommandButton className="h-10" onClick={onBack}>
              <RotateCcw className="size-3.5" />
              Reset
            </CommandButton>
            <CommandButton
              className={cn("h-10", draftSaved && "border-emerald-200 bg-emerald-50 text-emerald-700")}
              onClick={() => {
                setDraftSaved(true);
                window.setTimeout(() => setDraftSaved(false), 1200);
              }}
            >
              <Save className="size-3.5" />
              {draftSaved ? "Saved" : "Save Draft"}
            </CommandButton>
            <CommandButton
              className={cn("h-10", !publishEnabled && "bg-neutral-100 text-neutral-400 hover:bg-neutral-100")}
              disabled={!publishEnabled}
              tone={publishEnabled ? "dark" : "default"}
            >
              <Database className="size-3.5" />
              Publish
            </CommandButton>
          </div>
        </aside>
      </div>
    </div>
  );
}
