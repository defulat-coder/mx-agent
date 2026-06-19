"use client";

import { BookOpen, Download, Plus, RotateCcw, Search, X } from "lucide-react";
import { useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { TableResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type MemoryRow = Record<string, unknown>;

function text(row: MemoryRow, key: string, fallback = "-") {
  const value = row[key];
  return typeof value === "string" || typeof value === "number" ? String(value) : fallback;
}

function topics(row: MemoryRow) {
  const value = row.topics;
  return Array.isArray(value) ? value.map(String) : [];
}

function visibleTopics(row: MemoryRow) {
  const all = topics(row);
  return { hidden: Math.max(all.length - 3, 0), shown: all.slice(0, 3) };
}

export function MemoryPanel({ table }: { table: TableResponse }) {
  const [query, setQuery] = useState("");
  const [sortDesc, setSortDesc] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [exported, setExported] = useState(false);
  const [page, setPage] = useState("1");

  const rows = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    const filtered = normalized
      ? table.rows.filter((row) => {
          const haystack = [text(row, "content"), topics(row).join(" "), text(row, "user_id")]
            .join(" ")
            .toLowerCase();
          return haystack.includes(normalized);
        })
      : table.rows;
    return sortDesc ? filtered : [...filtered].reverse();
  }, [query, sortDesc, table.rows]);

  return (
    <div className="flex min-h-0 flex-1 flex-col px-5 py-5">
      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Memory</h1>
          <div className="mt-5 flex gap-6 text-sm">
            <div>
              <p className="mb-1 text-xs text-neutral-500">Database</p>
              <p className="whitespace-nowrap font-medium">{table.database}</p>
            </div>
            <div className="pt-6 font-mono text-neutral-500">/</div>
            <div>
              <p className="mb-1 text-xs text-neutral-500">Table</p>
              <p className="whitespace-nowrap font-medium">{table.table}</p>
            </div>
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <label className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-3.5 -translate-y-1/2 text-neutral-500" />
            <input
              className="h-9 w-60 rounded-md border border-neutral-200 bg-white pl-9 pr-3 font-mono text-[11px] outline-none placeholder:text-neutral-400 focus:border-neutral-400"
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search memories"
              value={query}
            />
          </label>
          <CommandButton
            className={cn("h-9 px-4", exported && "border-emerald-200 bg-emerald-50 text-emerald-700")}
            onClick={() => {
              setExported(true);
              window.setTimeout(() => setExported(false), 1400);
            }}
          >
            <Download className="size-3.5" />
            {exported ? "Exported" : "Export"}
          </CommandButton>
          <CommandButton className="h-9 px-4" onClick={() => setCreateOpen(true)} tone="dark">
            <Plus className="size-3.5" />
            Create Memory
          </CommandButton>
        </div>
      </div>

      <div className="relative min-h-0 flex-1 overflow-auto">
        <table className="min-w-[920px] w-full table-fixed border-collapse text-left text-sm">
          <thead>
            <tr className="sticky top-0 z-10 h-12 border-b border-neutral-100 bg-neutral-50 font-mono text-[11px] uppercase text-neutral-500">
              <th className="w-[50%] px-4 font-medium">Content</th>
              <th className="w-[30%] px-4 font-medium">Topics</th>
              <th className="w-[20%] px-4 text-right font-medium">
                <button
                  className="ml-auto flex items-center gap-1 uppercase"
                  onClick={() => setSortDesc((desc) => !desc)}
                  type="button"
                >
                  Updated at
                  <span className="text-[9px]">{sortDesc ? "↓" : "↑"}</span>
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => {
              const renderedTopics = visibleTopics(row);
              return (
                <tr className="h-14 border-b border-neutral-100 text-neutral-700" key={String(row.id ?? index)}>
                  <td className="truncate px-4 align-middle text-neutral-900">{text(row, "content")}</td>
                  <td className="px-4 align-middle">
                    <div className="flex min-w-0 flex-wrap gap-1">
                      {renderedTopics.shown.map((topic) => (
                        <span
                          className="rounded bg-neutral-100 px-1.5 py-0.5 font-mono text-[10px] uppercase text-neutral-700"
                          key={topic}
                        >
                          {topic}
                        </span>
                      ))}
                      {renderedTopics.hidden ? (
                        <span className="rounded bg-neutral-100 px-1.5 py-0.5 font-mono text-[10px] uppercase text-neutral-700">
                          +{renderedTopics.hidden}
                        </span>
                      ) : null}
                    </div>
                  </td>
                  <td className="truncate px-4 text-right align-middle text-neutral-600">{text(row, "updated_at")}</td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {rows.length === 0 ? (
          <div className="absolute inset-0 grid place-items-center bg-white/80">
            <div className="text-center">
              <BookOpen className="mx-auto mb-3 size-7 text-neutral-400" />
              <p className="text-2xl font-semibold">No memories found</p>
              <p className="mt-2 text-sm text-neutral-500">Create and view agent memories.</p>
              <div className="mt-4 flex justify-center gap-2">
                <CommandButton>
                  <BookOpen className="size-3.5" />
                  Learn More
                </CommandButton>
                <CommandButton onClick={() => setCreateOpen(true)} tone="dark">
                  <Plus className="size-3.5" />
                  Create Memory
                </CommandButton>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      <div className="flex h-12 items-center justify-end gap-2 border-t border-neutral-100 font-mono text-[11px] text-neutral-600">
        <input
          aria-label="Memory page"
          className="h-7 w-9 rounded-md border border-neutral-200 bg-white text-center outline-none focus:border-neutral-400"
          onChange={(event) => setPage(event.target.value)}
          value={page}
        />
        <span>/ 2</span>
        <CommandButton className="h-7 px-2" onClick={() => setPage("1")}>
          <RotateCcw className="size-3.5" />
          Reset
        </CommandButton>
      </div>

      {createOpen ? <CreateMemoryDialog onClose={() => setCreateOpen(false)} /> : null}
    </div>
  );
}

function CreateMemoryDialog({ onClose }: { onClose: () => void }) {
  const [topicInput, setTopicInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);

  const addTopic = () => {
    const topic = topicInput.trim();
    if (!topic || tags.includes(topic)) {
      return;
    }
    setTags((current) => [...current, topic]);
    setTopicInput("");
  };

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-white/55 backdrop-blur-sm">
      <div className="w-[672px] max-w-[calc(100vw-32px)] rounded-lg border border-neutral-200 bg-white p-6 shadow-xl">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Create Memory</h2>
          <button
            aria-label="Close dialog"
            className="grid size-8 place-items-center rounded-md text-neutral-600 hover:bg-neutral-100"
            onClick={onClose}
            type="button"
          >
            <X className="size-4" />
          </button>
        </div>

        <div className="space-y-5">
          <label className="block">
            <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">User ID</span>
            <input
              className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none placeholder:text-neutral-400 focus:border-neutral-400"
              placeholder="Enter user ID"
            />
          </label>
          <label className="block">
            <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Content</span>
            <textarea
              className="min-h-20 w-full resize-none rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none placeholder:text-neutral-400 focus:border-neutral-400"
              placeholder="Enter memory content"
            />
          </label>
          <div>
            <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Topics Optional</span>
            <div className="flex gap-2">
              <input
                className="h-9 flex-1 rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none placeholder:text-neutral-400 focus:border-neutral-400"
                onChange={(event) => setTopicInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    addTopic();
                  }
                }}
                placeholder="Type your topic and press enter to add it to the topic list"
                value={topicInput}
              />
              <button
                aria-label="Add tag"
                className="grid size-9 place-items-center rounded-md bg-neutral-100 text-neutral-500 transition-colors enabled:text-neutral-900 enabled:hover:bg-neutral-200 disabled:opacity-50"
                disabled={!topicInput.trim()}
                onClick={addTopic}
                type="button"
              >
                <Plus className="size-4" />
              </button>
            </div>
            {tags.length ? (
              <div className="mt-3 flex flex-wrap gap-1">
                {tags.map((tag) => (
                  <span
                    className="inline-flex items-center gap-1 rounded bg-neutral-100 px-2 py-1 font-mono text-[10px] uppercase text-neutral-700"
                    key={tag}
                  >
                    {tag}
                    <button
                      aria-label={`Remove ${tag}`}
                      className="text-neutral-500 hover:text-neutral-900"
                      onClick={() => setTags((current) => current.filter((item) => item !== tag))}
                      type="button"
                    >
                      <X className="size-3" />
                    </button>
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-2">
          <CommandButton className="h-10 bg-neutral-100" onClick={onClose}>
            Cancel
          </CommandButton>
          <CommandButton className="h-10" onClick={onClose} tone="dark">
            Create
          </CommandButton>
        </div>
      </div>
    </div>
  );
}
