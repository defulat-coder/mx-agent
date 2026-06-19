"use client";

import {
  BarChart3,
  Bot,
  ChevronDown,
  ChevronRight,
  Copy,
  Database,
  History,
  Info,
  Keyboard,
  MessageSquare,
  PanelRightClose,
  Paperclip,
  RotateCcw,
  Send,
  SlidersHorizontal,
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import { sendChatMessage } from "@/lib/agentos-api";
import { fallbackEntities } from "@/lib/agentos-data";
import type { ChatMessage, EntityCardData } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type EntityGroup = "agents" | "teams" | "workflows";
type Inspector = "config" | "sessions" | null;
type Menu = "group" | "entity" | null;

type ChatSurfaceProps = {
  initialGroup?: EntityGroup;
  initialEntityId?: string;
  initialSessionId?: string;
};

const groupLabels: Record<EntityGroup, string> = {
  agents: "Agents",
  teams: "Teams",
  workflows: "Workflows",
};

const groupTypeParams: Record<EntityGroup, string> = {
  agents: "agent",
  teams: "team",
  workflows: "workflow",
};

const promptSuggestions = [
  "What is Agno?",
  "Tell me about Learning Machines",
  "Summarize the key features of MX AgentOS",
];

const configSections = [
  {
    title: "Agent Details",
    rows: [
      ["Agent Id", "hr-agent"],
      ["Agent Name", "HR Assistant"],
    ],
  },
  {
    title: "Model",
    rows: [["Model", "glm-4-plus"]],
  },
  {
    title: "Database",
    rows: [["Storage", "mx-agent-db"]],
  },
  {
    title: "Tools",
    badge: "55",
    rows: [
      ["Domain", "HR"],
      ["Runnable", "true"],
    ],
  },
  {
    title: "Sessions",
    rows: [["Default", "enabled"]],
  },
  {
    title: "Default Tools",
    badge: "5",
    rows: [["Memory", "enabled"]],
  },
  {
    title: "System Message",
    rows: [["Scope", "Enterprise employee operations assistant."]],
  },
];

const agnoDeepLinkSessionId = "1534cf8b-ec92-40e3-91ed-2fb1e942267c";
const agnoRestoredMessages: ChatMessage[] = [
  {
    id: "agno-user-ai-trends",
    role: "user",
    content: "write insights on ai trends in 200 words",
  },
  {
    id: "agno-assistant-ai-trends",
    role: "assistant",
    stepLabel: "Finance Agent: Working...",
    content:
      "Artificial Intelligence (AI) continues to be a transformative force in 2024, with trends moving from isolated chatbots toward coordinated agent systems that can use tools, memory, and private knowledge. Enterprises are prioritizing domain-specific assistants for finance, HR, legal, IT, and customer operations because these workflows need auditable decisions, retrieval from trusted data, and human oversight. Multimodal models are also expanding how teams work with documents, images, voice, and dashboards, while smaller specialized models are improving cost control and latency. The next wave is less about replacing people and more about compressing routine analysis, routing, and follow-up work into reliable supervised processes. The winners will pair strong model capability with governance, evaluation, observability, and clear product experiences that make AI outputs easy to inspect and correct.",
  },
];

function sessionTitle(messages: ChatMessage[]) {
  const firstUserMessage = messages.find((message) => message.role === "user")?.content;
  if (!firstUserMessage) {
    return null;
  }
  return firstUserMessage.length > 30 ? `${firstUserMessage.slice(0, 27)}...` : firstUserMessage;
}

function getInitialEntity(group: EntityGroup, entityId?: string) {
  return fallbackEntities[group].find((entity) => entity.id === entityId) ?? fallbackEntities[group][0];
}

function isAgnoDeepLinkSession(group: EntityGroup, entityId: string, sessionId?: string) {
  return group === "teams" && entityId === "router-team" && sessionId === agnoDeepLinkSessionId;
}

function updateChatUrl(group: EntityGroup, entity: EntityCardData, sessionId?: string | null) {
  if (typeof window === "undefined") {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  params.set("type", groupTypeParams[group]);
  params.set("id", entity.id);
  if (sessionId) {
    params.set("session", sessionId);
  } else {
    params.delete("session");
  }
  window.history.replaceState(null, "", `/chat?${params.toString()}`);
}

export function ChatSurface({
  initialGroup = "agents",
  initialEntityId,
  initialSessionId,
}: ChatSurfaceProps) {
  const initialEntity = getInitialEntity(initialGroup, initialEntityId);
  const initialDeepLinkSession = isAgnoDeepLinkSession(initialGroup, initialEntity.id, initialSessionId);
  const [entityGroup, setEntityGroup] = useState<EntityGroup>(initialGroup);
  const [selectedEntity, setSelectedEntity] = useState<EntityCardData>(initialEntity);
  const [menu, setMenu] = useState<Menu>(null);
  const [inspector, setInspector] = useState<Inspector>(null);
  const [messages, setMessages] = useState<ChatMessage[]>(initialDeepLinkSession ? agnoRestoredMessages : []);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>(initialSessionId);
  const [isSending, setIsSending] = useState(false);
  const [showInactiveOverlay, setShowInactiveOverlay] = useState(initialDeepLinkSession);

  const availableEntities = fallbackEntities[entityGroup];
  const hasMessages = messages.length > 0;
  const activeSessionTitle = useMemo(() => sessionTitle(messages), [messages]);
  const placeholder = "Ask anything...";

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = input.trim();
    if (!message || isSending) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: message,
    };
    setShowInactiveOverlay(false);
    setMessages((current) => [...current, userMessage]);
    setInput("");
    setIsSending(true);
    const startedAt = Date.now();

    try {
      const response = await sendChatMessage(message, sessionId);
      setSessionId(response.session_id ?? sessionId);
      updateChatUrl(entityGroup, selectedEntity, response.session_id ?? sessionId);
      const durationSeconds = Math.max(1, Math.round((Date.now() - startedAt) / 1000));
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.reply,
          durationLabel: `Worked for ${durationSeconds} s`,
        },
      ]);
    } catch {
      const durationSeconds = Math.max(1, Math.round((Date.now() - startedAt) / 1000));
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: "The chat backend is not reachable from this browser session.",
          durationLabel: `Stopped after ${durationSeconds} s`,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  function selectGroup(nextGroup: EntityGroup) {
    const nextEntity = fallbackEntities[nextGroup][0];
    setEntityGroup(nextGroup);
    setSelectedEntity(nextEntity);
    setMenu(null);
    setMessages([]);
    setSessionId(undefined);
    setShowInactiveOverlay(false);
    updateChatUrl(nextGroup, nextEntity, null);
  }

  function selectEntity(entity: EntityCardData) {
    setSelectedEntity(entity);
    setMenu(null);
    setMessages([]);
    setSessionId(undefined);
    setShowInactiveOverlay(false);
    updateChatUrl(entityGroup, entity, null);
  }

  function startNewSession() {
    setMessages([]);
    setInput("");
    setSessionId(undefined);
    setInspector(null);
    setMenu(null);
    setShowInactiveOverlay(false);
    updateChatUrl(entityGroup, selectedEntity, null);
  }

  return (
    <div className="flex min-h-0 flex-1">
      <div className="flex min-w-0 flex-1 flex-col px-5 py-5">
        <div className="mb-4 flex items-center justify-between gap-4">
          <div className="relative flex min-w-0 items-center gap-2 text-sm">
            <span className="grid size-5 place-items-center rounded bg-[#ff3b25] text-xs text-white">A</span>
            <button
              className="inline-flex items-center gap-1.5 rounded-md px-1 py-1 font-medium hover:bg-neutral-100"
              onClick={() => setMenu(menu === "group" ? null : "group")}
              type="button"
            >
              {groupLabels[entityGroup]}
              <ChevronDown className="size-3.5" />
            </button>
            <span className="text-neutral-400">/</span>
            <button
              className="inline-flex items-center gap-1.5 rounded-md px-1 py-1 hover:bg-neutral-100"
              onClick={() => setMenu(menu === "entity" ? null : "entity")}
              type="button"
            >
              {selectedEntity.name}
              <ChevronDown className="size-3.5" />
            </button>
            {activeSessionTitle ? (
              <>
                <span className="text-neutral-400">/</span>
                <span className="max-w-56 truncate text-neutral-700">{activeSessionTitle}</span>
              </>
            ) : null}
            {menu === "group" ? (
              <Popover className="left-0 top-9 w-44">
                {(Object.keys(groupLabels) as EntityGroup[]).map((group) => (
                  <PopoverButton
                    active={group === entityGroup}
                    key={group}
                    onClick={() => selectGroup(group)}
                  >
                    {groupLabels[group]}
                  </PopoverButton>
                ))}
              </Popover>
            ) : null}
            {menu === "entity" ? (
              <Popover className="left-28 top-9 w-52">
                {availableEntities.map((entity) => (
                  <PopoverButton
                    active={entity.id === selectedEntity.id}
                    key={entity.id}
                    onClick={() => selectEntity(entity)}
                  >
                    {entity.name}
                  </PopoverButton>
                ))}
              </Popover>
            ) : null}
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <CommandButton aria-label="Keyboard shortcuts" className="px-2">
              <Keyboard className="size-3.5" />
            </CommandButton>
            {inspector ? (
              <>
                <CommandButton
                  aria-label="Configuration"
                  className={cn("px-2", inspector === "config" && "bg-neutral-200")}
                  onClick={() => {
                    setMenu(null);
                    setInspector(inspector === "config" ? null : "config");
                  }}
                >
                  <Info className="size-3.5" />
                </CommandButton>
                <CommandButton
                  aria-label="Sessions"
                  className={cn("px-2", inspector === "sessions" && "bg-neutral-200")}
                  onClick={() => {
                    setMenu(null);
                    setInspector(inspector === "sessions" ? null : "sessions");
                  }}
                >
                  <History className="size-3.5" />
                </CommandButton>
              </>
            ) : (
              <>
                <CommandButton
                  onClick={() => {
                    setMenu(null);
                    setInspector("config");
                  }}
                >
                  See Config
                </CommandButton>
                <CommandButton
                  onClick={() => {
                    setMenu(null);
                    setInspector("sessions");
                  }}
                >
                  Sessions
                </CommandButton>
              </>
            )}
            <CommandButton
              aria-label="Reset session"
              className="px-2"
              onClick={startNewSession}
            >
              <RotateCcw className="size-3.5" />
            </CommandButton>
            <CommandButton className="bg-neutral-500 text-white hover:bg-neutral-600" onClick={startNewSession}>
              + New Session
            </CommandButton>
          </div>
        </div>

        <div className="relative flex min-h-0 flex-1 flex-col">
          {!hasMessages ? (
            <div className="flex flex-1 items-center justify-center pb-36">
              <div className="text-center">
                <div className="mb-4 inline-flex size-8 items-center justify-center rounded-full">
                  <MessageIcon />
                </div>
                <h1 className="text-xl font-semibold">New Session</h1>
                <p className="mt-3 text-sm text-neutral-500">Enter your input to get started with your agent.</p>
                <div className="mt-10 flex flex-wrap justify-center gap-3">
                  {promptSuggestions.map((suggestion) => (
                    <button
                      className="rounded-full border border-neutral-200 bg-white px-5 py-2 text-sm text-neutral-700 shadow-sm hover:bg-neutral-50"
                      key={suggestion}
                      onClick={() => setInput(suggestion)}
                      type="button"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-7 overflow-auto px-2 pb-36 pt-8">
              {messages.map((message) =>
                message.role === "assistant" ? (
                  <div className="grid grid-cols-[28px_1fr] gap-3" key={message.id}>
                    <span className="grid size-6 place-items-center rounded-md bg-[#ff3b25] text-white">
                      <Bot className="size-3.5" />
                    </span>
                    <div className="min-w-0 space-y-3">
                    {message.stepLabel ? (
                      <details className="group text-sm" open>
                        <summary className="flex cursor-pointer list-none items-center gap-2 text-neutral-600">
                          <ChevronRight className="size-4 transition-transform group-open:rotate-90" />
                          {message.stepLabel}
                        </summary>
                        <div className="ml-6 mt-2 font-mono text-[11px] uppercase text-neutral-400">
                          Run started from restored session
                        </div>
                      </details>
                    ) : null}
                    {message.durationLabel ? (
                      <div className="flex items-center gap-2 text-sm text-neutral-500">
                        <ChevronDown className="size-4" />
                        {message.durationLabel}
                      </div>
                    ) : null}
                    <div className="text-sm leading-6 text-neutral-700">
                      {message.content}
                    </div>
                    <div className="flex items-center gap-3 text-neutral-500">
                      <button className="rounded p-1 hover:bg-neutral-100" type="button" aria-label="Copy response">
                        <Copy className="size-4" />
                      </button>
                      <button className="rounded p-1 hover:bg-neutral-100" type="button" aria-label="View run metrics">
                        <BarChart3 className="size-4" />
                      </button>
                    </div>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-[28px_1fr] gap-3" key={message.id}>
                    <span className="grid size-6 place-items-center rounded-md bg-neutral-100 font-mono text-[11px] text-neutral-700">
                      NN
                    </span>
                    <div className="text-sm leading-6 text-neutral-700">{message.content}</div>
                  </div>
                ),
              )}
              {isSending ? (
                <div className="grid grid-cols-[28px_1fr] gap-3">
                  <span className="grid size-6 place-items-center rounded-md bg-[#ff3b25] text-white">
                    <Bot className="size-3.5" />
                  </span>
                  <div className="flex items-center gap-2 text-sm text-neutral-500">
                    <ChevronRight className="size-4" />
                    Working...
                  </div>
                </div>
              ) : null}
            </div>
          )}

          {showInactiveOverlay ? (
            <AgentOsInactiveOverlay
              onDismiss={() => setShowInactiveOverlay(false)}
              onRefresh={() => window.location.reload()}
            />
          ) : null}

          <form
            className="absolute inset-x-0 bottom-2 mx-auto w-full max-w-3xl rounded-2xl border border-neutral-200 bg-white p-2 shadow-[0_10px_30px_rgba(0,0,0,0.12)]"
            onSubmit={onSubmit}
          >
            <textarea
              className="h-11 max-h-32 min-h-11 w-full resize-none rounded-xl bg-neutral-100 px-3 py-3 text-sm outline-none placeholder:text-neutral-400"
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  event.currentTarget.form?.requestSubmit();
                }
              }}
              placeholder={placeholder}
              rows={1}
              value={input}
            />
            <div className="mt-2 flex items-center justify-between">
              <div className="flex gap-2">
                <button className="grid size-8 place-items-center rounded-lg border border-neutral-200" type="button">
                  <Paperclip className="size-4" />
                </button>
                <button className="grid size-8 place-items-center rounded-lg border border-neutral-200" type="button">
                  <SlidersHorizontal className="size-4" />
                </button>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-mono text-[11px] uppercase">{selectedEntity.name}</span>
                <button
                  className="grid size-8 place-items-center rounded-lg bg-neutral-500 text-white disabled:opacity-50"
                  disabled={!input.trim() || isSending}
                  type="submit"
                >
                  <Send className="size-3.5" />
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {inspector === "config" ? (
        <ConfigInspector entity={selectedEntity} onClose={() => setInspector(null)} />
      ) : null}
      {inspector === "sessions" ? (
        <SessionsInspector messages={messages} onClose={() => setInspector(null)} />
      ) : null}
    </div>
  );
}

function AgentOsInactiveOverlay({
  onDismiss,
  onRefresh,
}: {
  onDismiss: () => void;
  onRefresh: () => void;
}) {
  return (
    <div className="absolute inset-x-0 top-1/2 z-20 mx-auto w-[min(92%,560px)] -translate-y-1/2 rounded-lg border border-neutral-200 bg-white px-8 py-7 text-center shadow-[0_18px_60px_rgba(0,0,0,0.18)]">
      <p className="mb-5 font-mono text-[11px] font-medium uppercase tracking-[0.14em] text-neutral-400">
        No teams available
      </p>
      <div className="mx-auto mb-4 grid size-10 place-items-center rounded-full bg-neutral-100">
        <Database className="size-5 text-neutral-500" />
      </div>
      <h2 className="text-lg font-semibold">AgentOS not active</h2>
      <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-neutral-500">
        Your AgentOS is connected but is not active. After running the AgentOS you need to refresh the page.
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        <a
          className="inline-flex h-9 items-center rounded-md border border-neutral-200 px-3 text-xs font-semibold uppercase hover:bg-neutral-50"
          href="https://docs.agno.com/agent-os/connect-your-os"
          rel="noreferrer"
          target="_blank"
        >
          Learn more
        </a>
        <button
          className="inline-flex h-9 items-center rounded-md border border-neutral-200 px-3 text-xs font-semibold uppercase hover:bg-neutral-50"
          onClick={onRefresh}
          type="button"
        >
          Refresh
        </button>
        <button
          className="inline-flex h-9 items-center rounded-md bg-neutral-900 px-3 text-xs font-semibold uppercase text-white hover:bg-neutral-700"
          onClick={onDismiss}
          type="button"
        >
          Explore a live demo AgentOS
        </button>
      </div>
      <p className="mt-5 text-xs text-red-500">Failed to connect to the AgentOS</p>
    </div>
  );
}

function Popover({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        "absolute z-30 rounded-md border border-neutral-200 bg-white p-1 text-sm shadow-lg",
        className,
      )}
    >
      {children}
    </div>
  );
}

function PopoverButton({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      className={cn(
        "flex h-9 w-full items-center rounded px-2 text-left text-sm hover:bg-neutral-100",
        active && "bg-neutral-100 font-medium",
      )}
      onClick={onClick}
      type="button"
    >
      {children}
    </button>
  );
}

function ConfigInspector({
  entity,
  onClose,
}: {
  entity: EntityCardData;
  onClose: () => void;
}) {
  return (
    <aside className="w-[500px] shrink-0 border-l border-neutral-200 bg-white px-4 py-5">
      <div className="mb-5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="grid size-5 place-items-center rounded bg-[#ff3b25] text-white">
            <Bot className="size-3" />
          </span>
          <h2 className="text-sm font-semibold">{entity.name}&apos;s Configuration</h2>
        </div>
        <button
          aria-label="Close configuration"
          className="grid size-7 place-items-center rounded-md text-neutral-500 hover:bg-neutral-100"
          onClick={onClose}
          type="button"
        >
          <PanelRightClose className="size-4" />
        </button>
      </div>

      <div className="space-y-4">
        {configSections.map((section, index) => (
          <details className="group" key={section.title} open={index === 0}>
            <summary className="flex cursor-pointer list-none items-center gap-2 text-sm font-medium">
              <ChevronRight className="size-4 transition-transform group-open:rotate-90" />
              {section.title}
              {section.badge ? (
                <span className="rounded-full bg-neutral-100 px-2 py-0.5 font-mono text-[11px] text-neutral-500">
                  {section.badge}
                </span>
              ) : null}
            </summary>
            <div className="ml-6 mt-3 rounded-xl bg-neutral-50 p-4 font-mono text-[11px] leading-7 text-neutral-700">
              {(section.title === "Agent Details"
                ? [
                    ["Agent Id", entity.id],
                    ["Agent Name", entity.name],
                  ]
                : section.rows
              ).map(([label, value]) => (
                <div className="grid grid-cols-[110px_1fr] gap-2" key={label}>
                  <span>{label}:</span>
                  <span>{String(value)}</span>
                </div>
              ))}
            </div>
          </details>
        ))}
      </div>
    </aside>
  );
}

function SessionsInspector({
  messages,
  onClose,
}: {
  messages: ChatMessage[];
  onClose: () => void;
}) {
  return (
    <aside className="w-[500px] shrink-0 border-l border-neutral-200 bg-white px-4 py-5">
      <div className="mb-8 flex items-center justify-between">
        <h2 className="text-sm font-semibold">Sessions</h2>
        <button
          aria-label="Close sessions"
          className="grid size-7 place-items-center rounded-md text-neutral-500 hover:bg-neutral-100"
          onClick={onClose}
          type="button"
        >
          <PanelRightClose className="size-4" />
        </button>
      </div>

      {messages.length === 0 ? (
        <div className="flex h-72 flex-col items-center justify-center rounded-xl bg-neutral-50 text-center">
          <div className="mb-8 flex -space-x-2">
            <span className="grid size-9 -rotate-12 place-items-center rounded-xl border border-neutral-200 bg-white shadow-sm">
              <MessageSquare className="size-5" />
            </span>
            <span className="grid size-9 rotate-12 place-items-center rounded-xl border border-red-100 bg-white text-[#ff3b25] shadow-sm">
              <Database className="size-5" />
            </span>
          </div>
          <p className="font-semibold">No session found</p>
          <p className="mt-3 max-w-64 text-sm leading-6 text-neutral-500">
            No session records yet. Start a conversation to create one.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          <button className="w-full rounded-lg border border-neutral-200 bg-neutral-50 p-3 text-left" type="button">
            <p className="text-sm font-medium">{messages[0]?.content}</p>
            <p className="mt-2 font-mono text-[11px] text-neutral-500">Active session</p>
          </button>
        </div>
      )}
    </aside>
  );
}

function MessageIcon() {
  return (
    <svg aria-hidden="true" className="size-6" fill="none" viewBox="0 0 24 24">
      <path d="M8 9h8M8 13h5" stroke="currentColor" strokeLinecap="round" strokeWidth="1.7" />
      <path
        d="M5.75 5.75h12.5v9.5h-4.7L10 18.25v-3H5.75z"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="1.7"
      />
    </svg>
  );
}
