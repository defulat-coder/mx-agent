"use client";

import { Keyboard, Paperclip, Send, SlidersHorizontal } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import { sendChatMessage } from "@/lib/agentos-api";
import type { ChatMessage } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

export function ChatSurface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [isSending, setIsSending] = useState(false);

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

  return (
    <div className="flex min-h-0 flex-1 flex-col px-5 py-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm">
          <span className="grid size-5 place-items-center rounded bg-[#ff3b25] text-xs text-white">A</span>
          <span className="font-medium">Agents</span>
          <span className="text-neutral-400">/</span>
          <span>Sage</span>
        </div>
        <div className="flex items-center gap-2">
          <CommandButton>
            <Keyboard className="size-3.5" />
          </CommandButton>
          <CommandButton>See Config</CommandButton>
          <CommandButton>Sessions</CommandButton>
          <CommandButton className="bg-neutral-500 text-white hover:bg-neutral-600">+ New Session</CommandButton>
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
              <button
                className="mt-10 rounded-full border border-neutral-100 px-5 py-2 text-sm text-neutral-300"
                type="button"
              >
                What is Agno?
              </button>
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
              <span className="font-mono text-[11px] uppercase">Sage</span>
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
