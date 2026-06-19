"use client";

import { ChevronDown, Plus, RefreshCw, Trash2, X } from "lucide-react";
import { useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { TableResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type KnowledgeRow = Record<string, unknown>;

type Collection = {
  id: string;
  name: string;
  database: string;
  table: string;
};

const collections: Collection[] = [
  {
    id: "clinic-records",
    name: "Clinic Records",
    database: "mx-agent-db",
    table: "clinic_records_contents",
  },
  {
    id: "hr-knowledge",
    name: "HR Knowledge",
    database: "mx-agent-db",
    table: "hr_knowledge_contents",
  },
  {
    id: "finance-knowledge",
    name: "Finance Knowledge",
    database: "mx-agent-db",
    table: "finance_knowledge_contents",
  },
  {
    id: "it-learnings",
    name: "IT Learnings",
    database: "mx-agent-db",
    table: "it_learnings_contents",
  },
];

function cellText(row: KnowledgeRow, key: string, fallback = "-") {
  const value = row[key];
  return typeof value === "string" || typeof value === "number" ? String(value) : fallback;
}

function metadataEntries(row: KnowledgeRow) {
  const value = row.metadata;
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return [];
  }
  return Object.entries(value).map(([key, entry]) => [key, String(entry)] as const);
}

function MetadataChips({ row }: { row: KnowledgeRow }) {
  const entries = metadataEntries(row);
  const visible = entries.slice(0, 1);
  const hidden = entries.length - visible.length;

  return (
    <div className="flex min-w-0 flex-wrap gap-1">
      {visible.map(([key, value]) => (
        <span
          className="rounded bg-neutral-100 px-1.5 py-0.5 font-mono text-[10px] uppercase text-neutral-700"
          key={key}
        >
          {key} = {value}
        </span>
      ))}
      {hidden > 0 ? (
        <span className="rounded bg-neutral-100 px-1.5 py-0.5 font-mono text-[10px] uppercase text-neutral-700">
          +{hidden}
        </span>
      ) : null}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className="font-mono text-[11px] uppercase text-neutral-900">
      {status}
    </span>
  );
}

export function KnowledgePanel({ table }: { table: TableResponse }) {
  const [collectionOpen, setCollectionOpen] = useState(false);
  const [selectedCollection, setSelectedCollection] = useState(collections[0]);
  const [selectedRowId, setSelectedRowId] = useState<string | null>(null);
  const [sortDesc, setSortDesc] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const rows = useMemo(() => {
    const normalized = table.rows.filter((row) => {
      const collection = cellText(row, "collection", selectedCollection.id);
      return collection === selectedCollection.id || selectedCollection.id === "clinic-records";
    });
    return sortDesc ? normalized : [...normalized].reverse();
  }, [selectedCollection.id, sortDesc, table.rows]);

  const selectedRow = useMemo(
    () => rows.find((row, index) => String(row.id ?? index) === selectedRowId) ?? null,
    [rows, selectedRowId],
  );

  const refresh = () => {
    setRefreshing(true);
    window.setTimeout(() => setRefreshing(false), 800);
  };

  return (
    <div className="flex min-h-0 flex-1">
      <div className="flex min-w-0 flex-1 flex-col px-5 py-5">
        <div className="mb-8 flex items-start justify-between gap-4">
          <h1 className="text-2xl font-semibold">Knowledge</h1>

          <div className="flex flex-wrap items-center justify-end gap-2">
            <CommandButton className="h-9 px-4" onClick={refresh}>
              <RefreshCw className={cn("size-3.5", refreshing && "animate-spin")} />
              Refresh
            </CommandButton>

            <div className="relative">
              <CommandButton
                aria-expanded={collectionOpen}
                className="h-9 min-w-44 justify-between px-4 normal-case"
                onClick={() => setCollectionOpen((open) => !open)}
              >
                <span>{selectedCollection.name}</span>
                <ChevronDown className="size-3.5" />
              </CommandButton>

              {collectionOpen ? (
                <div className="absolute right-0 top-11 z-30 w-72 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
                  {collections.map((collection) => (
                    <button
                      className={cn(
                        "w-full rounded px-3 py-2 text-left hover:bg-neutral-50",
                        collection.id === selectedCollection.id && "bg-neutral-50",
                      )}
                      key={collection.id}
                      onClick={() => {
                        setSelectedCollection(collection);
                        setCollectionOpen(false);
                        setSelectedRowId(null);
                      }}
                      type="button"
                    >
                      <span className="block text-sm font-medium text-neutral-900">{collection.name}</span>
                      <span className="mt-1 block font-mono text-[10px] uppercase text-neutral-500">
                        Db Id: {collection.database}
                      </span>
                      <span className="block font-mono text-[10px] uppercase text-neutral-500">
                        Table: {collection.table}
                      </span>
                    </button>
                  ))}
                </div>
              ) : null}
            </div>

            <CommandButton className="h-9 px-4 opacity-50" disabled>
              <Plus className="size-3.5" />
              Add Content
            </CommandButton>
          </div>
        </div>

        <div className="relative min-h-0 flex-1 overflow-auto">
          <table className="min-w-[960px] w-full table-fixed border-collapse text-left text-sm">
            <thead>
              <tr className="sticky top-0 z-10 h-12 border-b border-neutral-100 bg-white font-mono text-[11px] uppercase text-neutral-500">
                <th className="w-12 px-4 font-medium">
                  <span className="block size-4 rounded border border-neutral-300" />
                </th>
                <th className="w-[28%] px-4 font-medium">Name</th>
                <th className="w-[16%] px-4 font-medium">Content type</th>
                <th className="w-[26%] px-4 font-medium">Metadata</th>
                <th className="w-[14%] px-4 font-medium">Status</th>
                <th className="w-[16%] px-4 text-right font-medium">
                  <button
                    className="ml-auto flex items-center gap-1 uppercase"
                    onClick={() => setSortDesc((desc) => !desc)}
                    type="button"
                  >
                    Updated at
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => {
                const id = String(row.id ?? index);
                const selected = id === selectedRowId;
                return (
                  <tr
                    className={cn(
                      "h-14 cursor-pointer border-b border-neutral-100 text-neutral-700 hover:bg-neutral-50",
                      selected && "bg-neutral-50",
                    )}
                    key={id}
                    onClick={() => {
                      setCollectionOpen(false);
                      setSelectedRowId(selected ? null : id);
                    }}
                  >
                    <td className="px-4 align-middle">
                      <span className={cn("block size-4 rounded border", selected ? "border-neutral-950 bg-neutral-950" : "border-neutral-300")} />
                    </td>
                    <td className="truncate px-4 align-middle text-neutral-900">{cellText(row, "name")}</td>
                    <td className="px-4 align-middle">{cellText(row, "content_type")}</td>
                    <td className="px-4 align-middle">
                      <MetadataChips row={row} />
                    </td>
                    <td className="px-4 align-middle">
                      <StatusBadge status={cellText(row, "status")} />
                    </td>
                    <td className="truncate px-4 text-right align-middle text-neutral-600">
                      {cellText(row, "updated_at")}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {selectedRow ? (
        <KnowledgeInspector
          collection={selectedCollection}
          onClose={() => setSelectedRowId(null)}
          row={selectedRow}
        />
      ) : null}
    </div>
  );
}

function KnowledgeInspector({
  collection,
  onClose,
  row,
}: {
  collection: Collection;
  onClose: () => void;
  row: KnowledgeRow;
}) {
  const [name, setName] = useState(cellText(row, "name"));
  const [description, setDescription] = useState(cellText(row, "description", ""));
  const dirty = name !== cellText(row, "name") || description !== cellText(row, "description", "");

  return (
    <aside className="flex w-[420px] shrink-0 flex-col border-l border-neutral-200 bg-white">
      <div className="flex items-start justify-between border-b border-neutral-100 px-4 py-5">
        <div className="min-w-0">
          <p className="truncate font-mono text-[11px] uppercase text-neutral-500">{collection.name}</p>
          <h2 className="mt-1 truncate text-sm font-semibold">{cellText(row, "name")}</h2>
        </div>
        <button
          aria-label="Close details"
          className="grid size-8 place-items-center rounded-md text-neutral-600 hover:bg-neutral-100"
          onClick={onClose}
          type="button"
        >
          <X className="size-4" />
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-auto px-4 py-5">
        <label className="block">
          <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Name</span>
          <input
            className="h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-neutral-400"
            onChange={(event) => setName(event.target.value)}
            value={name}
          />
        </label>

        <label className="mt-5 block">
          <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Description Optional</span>
          <textarea
            className="min-h-20 w-full resize-none rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
            onChange={(event) => setDescription(event.target.value)}
            value={description}
          />
        </label>

        <div className="mt-5">
          <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Metadata</span>
          <div className="rounded-md border border-neutral-200 bg-neutral-50">
            {metadataEntries(row).map(([key, value]) => (
              <div className="grid grid-cols-[120px_1fr] border-b border-neutral-200 px-3 py-2 last:border-b-0" key={key}>
                <span className="font-mono text-[11px] uppercase text-neutral-500">{key}</span>
                <span className="min-w-0 break-words font-mono text-[11px] uppercase text-neutral-900">{value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-4">
          <div>
            <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Content Type</span>
            <p className="h-9 rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm">
              {cellText(row, "content_type")}
            </p>
          </div>
          <div>
            <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Status</span>
            <p className="h-9 rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2 font-mono text-[11px] uppercase">
              {cellText(row, "status")}
            </p>
          </div>
        </div>

        <div className="mt-5">
          <span className="mb-2 block font-mono text-[11px] uppercase text-neutral-500">Updated At</span>
          <p className="h-9 rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm">
            {cellText(row, "updated_at")}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 border-t border-neutral-100 p-4">
        <CommandButton className="h-10 border-red-200 bg-red-50 text-red-700 hover:bg-red-100">
          <Trash2 className="size-3.5" />
          Delete
        </CommandButton>
        <CommandButton className="h-10" onClick={onClose}>
          Cancel
        </CommandButton>
        <CommandButton
          className={cn("h-10", !dirty && "bg-neutral-100 text-neutral-400 hover:bg-neutral-100")}
          disabled={!dirty}
          tone={dirty ? "dark" : "default"}
        >
          Save
        </CommandButton>
      </div>
    </aside>
  );
}
