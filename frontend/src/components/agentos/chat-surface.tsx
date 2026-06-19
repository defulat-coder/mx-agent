"use client";

import {
  Bot,
  ChevronDown,
  ChevronRight,
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

const groupLabels: Record<EntityGroup, string> = {
  agents: "Agents",
  teams: "Teams",
  workflows: "Workflows",
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

export function ChatSurface() {
  const [entityGroup, setEntityGroup] = useState<EntityGroup>("agents");
  const [selectedEntity, setSelectedEntity] = useState<EntityCardData>(fallbackEntities.agents[0]);
  const [menu, setMenu] = useState<Menu>(null);
  const [inspector, setInspector] = useState<Inspector>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [isSending, setIsSending] = useState(false);

  const availableEntities = fallbackEntities[entityGroup];
  const hasMessages = messages.length > 0;
  const placeholder = useMemo(
    () => (hasMessages ? "Ask a follow-up..." : "Ask anything..."),
    [hasMessages],
  );

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
    setMessages((current) => [...current, userMessage]);
    setInput("");
    setIsSending(true);

    try {
      const response = await sendChatMessage(message, sessionId);
      setSessionId(response.session_id ?? sessionId);
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.reply,
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: "The chat backend is not reachable from this browser session.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  function selectGroup(nextGroup: EntityGroup) {
    setEntityGroup(nextGroup);
    setSelectedEntity(fallbackEntities[nextGroup][0]);
    setMenu(null);
    setMessages([]);
    setSessionId(undefined);
  }

  function selectEntity(entity: EntityCardData) {
    setSelectedEntity(entity);
    setMenu(null);
    setMessages([]);
    setSessionId(undefined);
  }

  function startNewSession() {
    setMessages([]);
    setInput("");
    setSessionId(undefined);
    setInspector(null);
    setMenu(null);
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
            <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-3 overflow-auto px-2 pb-36 pt-8">
              {messages.map((message) => (
                <div
                  className={cn(
                    "max-w-[78%] rounded-lg px-3 py-2 text-sm leading-6",
                    message.role === "user"
                      ? "ml-auto bg-neutral-950 text-white"
                      : "mr-auto border border-neutral-200 bg-white text-neutral-700",
                  )}
                  key={message.id}
                >
                  {message.content}
                </div>
              ))}
            </div>
          )}

          <form
            className="absolute inset-x-0 bottom-2 mx-auto w-full max-w-3xl rounded-2xl border border-neutral-200 bg-white p-2 shadow-[0_10px_30px_rgba(0,0,0,0.12)]"
            onSubmit={onSubmit}
          >
            <input
              className="h-11 w-full rounded-xl bg-neutral-100 px-3 text-sm outline-none placeholder:text-neutral-400"
              onChange={(event) => setInput(event.target.value)}
              placeholder={placeholder}
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
