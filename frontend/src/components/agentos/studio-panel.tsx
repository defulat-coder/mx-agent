"use client";

import { Bot, Check, ChevronDown, Database, MessageSquare, Pencil, Plus, RotateCcw, Save, X } from "lucide-react";
import { useMemo, useState } from "react";
import type { ReactNode } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { EntityCardData } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type StudioMode = "list" | "builder";

const models = [
  "claude-haiku-4-5-20251001 (Anthropic)",
  "claude-opus-4-6 (Anthropic)",
  "claude-opus-4-7 (Anthropic)",
  "claude-sonnet-4-6 (Anthropic)",
  "gemini-3-flash-preview (Google)",
  "gemini-3.1-flash-lite-preview (Google)",
  "gemini-3.1-pro-preview (Google)",
  "gpt-5.4-mini (OpenAI)",
  "gpt-5.5 (OpenAI)",
];

const toolOptions = [
  "MCPTools",
  "add_task",
  "agenda",
  "arxiv_tools",
  "book_flight",
  "calculator",
  "charge_payment",
  "check_formulary",
  "coding_tools",
  "file_generation",
  "file_tools",
  "generate_report",
  "get_email_digest",
  "get_summary",
];

const sessionSummaryManagers = ["None", "session_summary_manager_d2342bdc", "session_summary_manager_ff4bf520"];
const knowledgeOptions = ["None", "Clinic Records", "Coach Learnings", "Dash Knowledge", "Dash Learnings", "Investment Knowledge"];
const memoryManagers = [
  "None",
  "memory_manager_542da8f2",
  "memory_manager_6db1ecc0",
  "memory_manager_6f76bc67",
  "memory_manager_8defbe13",
  "memory_manager_befdbdb0",
];

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
  const [model, setModel] = useState(agent ? models[0] : "");
  const [instructions, setInstructions] = useState(agent?.description ?? "");
  const [activeSection, setActiveSection] = useState("Basics");
  const [openSections, setOpenSections] = useState<Set<string>>(() => new Set(["Basics"]));
  const [toolsOpen, setToolsOpen] = useState(false);
  const [selectedTools, setSelectedTools] = useState<string[]>([]);
  const [historyRuns, setHistoryRuns] = useState("");
  const [sessionSummaryManager, setSessionSummaryManager] = useState("");
  const [addHistory, setAddHistory] = useState(false);
  const [enableSummaries, setEnableSummaries] = useState(false);
  const [addSummary, setAddSummary] = useState(false);
  const [sessionState, setSessionState] = useState("{}");
  const [addSessionState, setAddSessionState] = useState(false);
  const [enableAgenticState, setEnableAgenticState] = useState(false);
  const [knowledge, setKnowledge] = useState("");
  const [addKnowledge, setAddKnowledge] = useState(false);
  const [searchKnowledge, setSearchKnowledge] = useState(false);
  const [memoryManager, setMemoryManager] = useState("");
  const [enableAgenticMemory, setEnableAgenticMemory] = useState(false);
  const [updateMemoryOnRun, setUpdateMemoryOnRun] = useState(false);
  const [addMemories, setAddMemories] = useState(false);
  const [agentId, setAgentId] = useState("");
  const [metadata, setMetadata] = useState("{}");
  const [configJson, setConfigJson] = useState("");
  const [draftSaved, setDraftSaved] = useState(false);
  const [published, setPublished] = useState(false);

  const publishEnabled = name.trim().length > 0 || selectedTools.length > 0;
  const preview = useMemo(
    () => [
      ["Name", name.trim() || "No name given yet"],
      ["Model", model || "No model given yet"],
      ["Instructions", instructions.trim() || "No instructions given yet"],
      ["Tools", selectedTools.length > 0 ? selectedTools.join(", ") : "No tools given yet"],
      ["Database", "demo-os-db"],
    ],
    [instructions, model, name, selectedTools],
  );

  const openSection = (section: string) => {
    setActiveSection(section);
    setOpenSections((current) => new Set(current).add(section));
  };

  const resetBuilder = () => {
    setName(agent?.name ?? "");
    setModel(agent ? models[0] : "");
    setInstructions(agent?.description ?? "");
    setSelectedTools([]);
    setHistoryRuns("");
    setSessionSummaryManager("");
    setAddHistory(false);
    setEnableSummaries(false);
    setAddSummary(false);
    setSessionState("{}");
    setAddSessionState(false);
    setEnableAgenticState(false);
    setKnowledge("");
    setAddKnowledge(false);
    setSearchKnowledge(false);
    setMemoryManager("");
    setEnableAgenticMemory(false);
    setUpdateMemoryOnRun(false);
    setAddMemories(false);
    setAgentId("");
    setMetadata("{}");
    setConfigJson("");
    setPublished(false);
    setToolsOpen(false);
    setOpenSections(new Set(["Basics"]));
    setActiveSection("Basics");
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex h-14 shrink-0 items-center gap-2 px-5 text-sm font-semibold">
        <button className="inline-flex items-center gap-2 hover:text-neutral-600" onClick={onBack} type="button">
          <span aria-hidden className="text-lg leading-none">
            ‹
          </span>
          Agents
        </button>
        <span className="text-neutral-300">/</span>
        <span>{agent ? agent.name : "New Agent"}</span>
      </div>
      <div className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_420px]">
        <div className="agno-scrollbar min-h-0 overflow-auto px-5 py-5">
          <div className="space-y-2">
            <BuilderSection
              active={activeSection === "Basics"}
              description="Configure the core identity and behaviour of your agent"
              open={openSections.has("Basics")}
              onOpen={() => openSection("Basics")}
              title="Basics"
            >
              <label className="block">
                <FieldLabel label="Agent Name" />
                <input
                  className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none placeholder:text-neutral-400 focus:border-neutral-400"
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Enter agent name"
                  value={name}
                />
              </label>

              <label className="block">
                <FieldLabel label="Model" />
                <select
                  className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-neutral-400"
                  onChange={(event) => setModel(event.target.value)}
                  value={model}
                >
                  <option value="">Select a model</option>
                  {models.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <FieldLabel label="Instructions" optional />
                <textarea
                  className="min-h-24 w-full resize-none rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none placeholder:text-neutral-400 focus:border-neutral-400"
                  onChange={(event) => setInstructions(event.target.value)}
                  placeholder="Enter instructions"
                  value={instructions}
                />
              </label>

              <div>
                <FieldLabel label="Tools" optional />
                <div className="relative">
                  <button
                    aria-expanded={toolsOpen}
                    className="flex min-h-9 w-full items-center justify-between gap-3 rounded-md border border-neutral-200 bg-white px-3 py-2 text-left text-sm text-neutral-600"
                    onClick={() => setToolsOpen((open) => !open)}
                    type="button"
                  >
                    <span>Select tools</span>
                    <span className="flex flex-wrap justify-end gap-1 font-mono text-[11px] uppercase">
                      {selectedTools.length > 0 ? selectedTools.join(", ") : "No tools selected"}
                    </span>
                  </button>
                  {toolsOpen ? (
                    <div className="absolute left-0 top-11 z-20 max-h-72 w-full overflow-auto rounded-md border border-neutral-200 bg-white p-1 text-sm shadow-lg">
                      <div role="listbox" aria-label="Suggestions">
                        {toolOptions.map((tool) => {
                          const selected = selectedTools.includes(tool);

                          return (
                            <button
                              className={cn("flex h-8 w-full items-center gap-2 rounded px-2 text-left hover:bg-neutral-100", selected && "bg-neutral-100")}
                              key={tool}
                              onClick={() => {
                                setSelectedTools((current) =>
                                  selected ? current.filter((item) => item !== tool) : [...current, tool],
                                );
                              }}
                              role="option"
                              aria-selected={selected}
                              type="button"
                            >
                              <span
                                aria-hidden
                                className={cn(
                                  "grid size-4 place-items-center rounded border border-neutral-300 bg-white",
                                  selected && "border-neutral-950 bg-neutral-950 text-white",
                                )}
                              >
                                {selected ? <Check className="size-3" /> : null}
                              </span>
                              <span>{tool}</span>
                            </button>
                          );
                        })}
                        <div className="px-2 py-2 text-xs text-neutral-500">Loading more...</div>
                      </div>
                    </div>
                  ) : null}
                </div>
                {selectedTools.length > 0 ? (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {selectedTools.map((tool) => (
                      <button
                        className="inline-flex h-6 items-center gap-1 rounded-md border border-neutral-200 bg-neutral-50 px-2 font-mono text-[11px] uppercase"
                        key={tool}
                        onClick={() => setSelectedTools((current) => current.filter((item) => item !== tool))}
                        type="button"
                      >
                        {tool}
                        <X className="size-3" />
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>

              <label className="block">
                <FieldLabel label="Database" optional />
                <select
                  className="h-9 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm text-neutral-500 outline-none"
                  disabled
                  value="demo-os-db"
                >
                  <option>demo-os-db</option>
                </select>
                <span className="mt-2 block text-xs text-neutral-500">In demo mode, the database is auto-selected.</span>
              </label>
            </BuilderSection>

            <BuilderSection
              active={activeSection === "Context Management"}
              description="Control the information sent to language models"
              open={openSections.has("Context Management")}
              onOpen={() => openSection("Context Management")}
              title="Context Management"
            >
              <label className="block">
                <FieldLabel label="Number of History Runs" optional />
                <input
                  className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-neutral-400"
                  min={0}
                  onChange={(event) => setHistoryRuns(event.target.value)}
                  type="number"
                  value={historyRuns}
                />
                <span className="mt-2 block text-xs text-neutral-500">Number of historical runs to include in the messages</span>
              </label>
              <SelectField
                label="Session Summary Manager"
                onChange={setSessionSummaryManager}
                options={sessionSummaryManagers}
                optional
                placeholder="Select a session summary manager"
                value={sessionSummaryManager}
              />
              <SwitchRow checked={addHistory} label="Add History to Context" onChange={setAddHistory} />
              <SwitchRow checked={enableSummaries} label="Enable Session Summaries" onChange={setEnableSummaries} />
              <SwitchRow checked={addSummary} label="Add Session Summary to Context" onChange={setAddSummary} />
            </BuilderSection>

            <BuilderSection
              active={activeSection === "Session State"}
              description="Session state configuration"
              open={openSections.has("Session State")}
              onOpen={() => openSection("Session State")}
              title="Session State"
            >
              <JsonEditor label="Session State" onChange={setSessionState} value={sessionState} />
              <SwitchRow checked={addSessionState} label="Add Session State to Context" onChange={setAddSessionState} />
              <SwitchRow checked={enableAgenticState} label="Enable Agentic State" onChange={setEnableAgenticState} />
            </BuilderSection>

            <BuilderSection
              active={activeSection === "Knowledge"}
              description="Knowledge base configuration for retrieval"
              open={openSections.has("Knowledge")}
              onOpen={() => openSection("Knowledge")}
              title="Knowledge"
            >
              <SelectField
                label="Knowledge"
                onChange={setKnowledge}
                options={knowledgeOptions}
                optional
                placeholder="Select knowledge"
                value={knowledge}
              />
              <SwitchRow checked={addKnowledge} label="Add Knowledge to Context" onChange={setAddKnowledge} />
              <SwitchRow checked={searchKnowledge} label="Search Knowledge" onChange={setSearchKnowledge} />
            </BuilderSection>

            <BuilderSection
              active={activeSection === "Memory"}
              description="Long-term user memory management"
              open={openSections.has("Memory")}
              onOpen={() => openSection("Memory")}
              title="Memory"
            >
              <SelectField
                label="Memory Manager"
                onChange={setMemoryManager}
                options={memoryManagers}
                optional
                placeholder="Select a memory manager"
                value={memoryManager}
              />
              <SwitchRow checked={enableAgenticMemory} label="Enable Agentic Memory" onChange={setEnableAgenticMemory} />
              <p className="text-center font-mono text-[11px] uppercase text-neutral-500">Or</p>
              <SwitchRow checked={updateMemoryOnRun} label="Update Memory on Run" onChange={setUpdateMemoryOnRun} />
              <SwitchRow checked={addMemories} label="Add Memories to Context" onChange={setAddMemories} />
            </BuilderSection>

            <BuilderSection
              active={activeSection === "Advanced"}
              description="Additional configuration as JSON"
              open={openSections.has("Advanced")}
              onOpen={() => openSection("Advanced")}
              title="Advanced"
            >
              <label className="block">
                <FieldLabel label="Agent ID" optional />
                <input
                  className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none placeholder:text-neutral-400 focus:border-neutral-400"
                  onChange={(event) => setAgentId(event.target.value)}
                  placeholder="Auto-generated if not provided"
                  value={agentId}
                />
              </label>
              <JsonEditor label="Metadata" onChange={setMetadata} value={metadata} />
              <label className="block">
                <FieldLabel label="Config JSON" optional />
                <textarea
                  className="min-h-24 w-full resize-none rounded-md border border-neutral-200 bg-white px-3 py-2 font-mono text-xs outline-none placeholder:text-neutral-400 focus:border-neutral-400"
                  onChange={(event) => setConfigJson(event.target.value)}
                  placeholder='{"cache_session": true, "enable_user_memories": true, "compress_tool_results": false}'
                  value={configJson}
                />
                <span className="mt-2 block text-xs text-neutral-500">
                  Pass any additional advanced configuration as JSON. See Agent documentation for all available parameters.
                </span>
              </label>
            </BuilderSection>
          </div>
        </div>

        <aside className="flex min-h-0 flex-col border-l border-neutral-200 bg-white">
          <div className="border-b border-neutral-100 px-4 py-5">
            <p className="font-mono text-[11px] uppercase text-neutral-500">{name.trim() || "Name of agent"}</p>
            <h2 className="mt-1 text-sm font-semibold">Basics</h2>
          </div>
          <div className="min-h-0 flex-1 overflow-auto px-4 py-4">
            <div className="rounded-lg bg-white p-4">
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
            <CommandButton className="h-10" onClick={resetBuilder}>
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
              className={cn(
                "h-10",
                !publishEnabled && "bg-neutral-100 text-neutral-400 hover:bg-neutral-100",
                published && "border-emerald-700 bg-emerald-700 text-white hover:bg-emerald-700",
              )}
              disabled={!publishEnabled}
              onClick={() => setPublished(true)}
              tone={publishEnabled ? "dark" : "default"}
            >
              <Database className="size-3.5" />
              {published ? "Published" : "Publish"}
            </CommandButton>
          </div>
        </aside>
      </div>
    </div>
  );
}

function BuilderSection({
  active,
  children,
  description,
  onOpen,
  open,
  title,
}: {
  active: boolean;
  children: ReactNode;
  description: string;
  onOpen: () => void;
  open: boolean;
  title: string;
}) {
  return (
    <section className={cn("rounded-lg border border-neutral-200 bg-white", active && "bg-neutral-50")}>
      <button className="flex w-full items-center justify-between px-4 py-4 text-left" onClick={onOpen} type="button">
        <span>
          <span className="block text-sm font-semibold">{title}</span>
          <span className="mt-1 block text-xs text-neutral-500">{description}</span>
        </span>
        <ChevronDown className={cn("size-4 transition-transform", open && "rotate-180")} />
      </button>
      {open ? <div className="space-y-5 border-t border-neutral-100 px-4 py-5">{children}</div> : null}
    </section>
  );
}

function FieldLabel({ label, optional = false }: { label: string; optional?: boolean }) {
  return (
    <span className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase text-neutral-500">
      {label}
      {optional ? <span className="text-neutral-400">Optional</span> : null}
    </span>
  );
}

function SelectField({
  label,
  onChange,
  options,
  optional = false,
  placeholder,
  value,
}: {
  label: string;
  onChange: (value: string) => void;
  options: string[];
  optional?: boolean;
  placeholder: string;
  value: string;
}) {
  return (
    <label className="block">
      <FieldLabel label={label} optional={optional} />
      <select
        className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-neutral-400"
        onChange={(event) => onChange(event.target.value)}
        value={value}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function SwitchRow({ checked, label, onChange }: { checked: boolean; label: string; onChange: (checked: boolean) => void }) {
  return (
    <button
      className="flex w-full items-center justify-between gap-4 rounded-md border border-neutral-200 bg-white px-3 py-2 text-left hover:bg-neutral-50"
      onClick={() => onChange(!checked)}
      role="switch"
      aria-checked={checked}
      type="button"
    >
      <span className="font-mono text-[11px] uppercase text-neutral-600">{label}</span>
      <span className={cn("flex h-5 w-9 items-center rounded-full p-0.5 transition-colors", checked ? "bg-neutral-950" : "bg-neutral-200")}>
        <span className={cn("size-4 rounded-full bg-white transition-transform", checked && "translate-x-4")} />
      </span>
    </button>
  );
}

function JsonEditor({ label, onChange, value }: { label: string; onChange: (value: string) => void; value: string }) {
  return (
    <label className="block">
      <div className="mb-2 flex items-center justify-between">
        <span className="font-mono text-[11px] uppercase text-neutral-500">{label}</span>
        <CommandButton className="h-6 px-2 opacity-50" disabled>
          Format
        </CommandButton>
      </div>
      <textarea
        className="min-h-24 w-full resize-none rounded-md border border-neutral-200 bg-white px-3 py-2 font-mono text-xs outline-none placeholder:text-neutral-400 focus:border-neutral-400"
        onChange={(event) => onChange(event.target.value)}
        placeholder="{}"
        value={value}
      />
    </label>
  );
}
