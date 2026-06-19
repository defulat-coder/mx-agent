"use client";

import { CheckSquare, Download, ExternalLink, Filter, PanelRightClose } from "lucide-react";
import { useMemo, useState } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import type { TableResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

function renderValue(value: unknown) {
  if (Array.isArray(value)) {
    return (
      <div className="flex flex-wrap gap-1">
        {value.map((item) => (
          <span className="rounded bg-neutral-100 px-1.5 py-0.5 font-mono text-[11px]" key={String(item)}>
            {String(item)}
          </span>
        ))}
      </div>
    );
  }

  if (typeof value === "boolean") {
    return value ? <CheckSquare className="size-4 text-neutral-700" /> : "-";
  }

  if (typeof value === "object" && value !== null) {
    return <span className="font-mono text-[11px]">{JSON.stringify(value)}</span>;
  }

  return String(value ?? "-");
}

export function DataTable({ table }: { table: TableResponse }) {
  const [filterOpen, setFilterOpen] = useState(false);
  const [filter, setFilter] = useState(table.filters[0] ?? "View: All");
  const [selectedRowId, setSelectedRowId] = useState<string | null>(null);
  const [exported, setExported] = useState(false);

  const selectedRow = useMemo(
    () => table.rows.find((row, index) => String(row.id ?? index) === selectedRowId) ?? null,
    [selectedRowId, table.rows],
  );

  const filterOptions = useMemo(() => {
    const extras = table.title === "Knowledge" ? ["Status: Completed", "Content: File"] : ["Updated At: Desc"];
    return Array.from(new Set([...(table.filters.length ? table.filters : ["View: All"]), ...extras]));
  }, [table.filters, table.title]);

  return (
    <div className="flex min-h-0 flex-1">
      <div className="flex min-w-0 flex-1 flex-col px-5 py-5">
        <div className="mb-8 flex items-start justify-between gap-4">
          <div className="flex gap-6 text-sm">
            <div>
              <p className="mb-1 text-xs text-neutral-500">Database</p>
              <p className="font-medium">{table.database}</p>
            </div>
            <div className="pt-6 font-mono text-neutral-500">/</div>
            <div>
              <p className="mb-1 text-xs text-neutral-500">Table</p>
              <p className="font-medium">{table.table}</p>
            </div>
          </div>
          <div className="relative flex items-center gap-2">
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
            <CommandButton className="h-9 justify-between px-4 normal-case" onClick={() => setFilterOpen((open) => !open)}>
              <Filter className="size-3.5" />
              <span>{filter}</span>
              <span className="ml-10 text-[9px]">▼</span>
            </CommandButton>
            {filterOpen ? (
              <div className="absolute right-0 top-11 z-20 w-52 rounded-md border border-neutral-200 bg-white p-1 shadow-lg">
                {filterOptions.map((option) => (
                  <button
                    className={cn(
                      "flex h-9 w-full items-center rounded px-2 text-left text-sm hover:bg-neutral-100",
                      option === filter && "bg-neutral-100 font-medium",
                    )}
                    key={option}
                    onClick={() => {
                      setFilter(option);
                      setFilterOpen(false);
                    }}
                    type="button"
                  >
                    {option}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
        </div>

        <div className="relative min-h-0 flex-1 overflow-auto">
          {table.rows.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <p className="text-2xl font-semibold">No records found</p>
                <p className="mt-2 text-sm text-neutral-500">This table does not have any rows for the selected view.</p>
              </div>
            </div>
          ) : null}
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-neutral-100 text-[11px] text-neutral-500">
                <th className="w-12 px-4 py-3 font-mono font-medium">
                  <span className="block size-4 rounded border border-neutral-300" />
                </th>
                {table.columns.map((column) => (
                  <th className="px-4 py-3 font-mono font-medium" key={column.key}>
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.rows.map((row, index) => {
                const id = String(row.id ?? index);
                const selected = id === selectedRowId;

                return (
                  <tr
                    className={cn(
                      "cursor-pointer border-b border-neutral-100 text-neutral-700 hover:bg-neutral-50",
                      selected && "bg-neutral-50",
                    )}
                    key={id}
                    onClick={() => {
                      setFilterOpen(false);
                      setSelectedRowId(selected ? null : id);
                    }}
                  >
                    <td className="px-4 py-4">
                      <span className={cn("block size-4 rounded border", selected ? "border-neutral-900 bg-neutral-900" : "border-neutral-300")} />
                    </td>
                    {table.columns.map((column) => (
                      <td
                        className={cn("px-4 py-4 align-middle", column.mono && "font-mono text-xs")}
                        key={column.key}
                      >
                        {renderValue(row[column.key])}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {selectedRow ? (
        <TableInspector
          columns={table.columns}
          onClose={() => setSelectedRowId(null)}
          row={selectedRow}
          title={table.title}
        />
      ) : null}
    </div>
  );
}

function TableInspector({
  columns,
  onClose,
  row,
  title,
}: {
  columns: TableResponse["columns"];
  onClose: () => void;
  row: Record<string, unknown>;
  title: string;
}) {
  return (
    <aside className="w-[420px] shrink-0 border-l border-neutral-200 bg-white px-4 py-5">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="font-mono text-[11px] uppercase text-neutral-500">{title}</p>
          <h2 className="mt-1 text-sm font-semibold">Row Details</h2>
        </div>
        <button
          aria-label="Close details"
          className="grid size-7 place-items-center rounded-md text-neutral-500 hover:bg-neutral-100"
          onClick={onClose}
          type="button"
        >
          <PanelRightClose className="size-4" />
        </button>
      </div>

      <div className="rounded-xl bg-neutral-50 p-4">
        {columns.map((column) => (
          <div className="border-b border-neutral-200/70 py-3 last:border-0" key={column.key}>
            <p className="mb-1 font-mono text-[11px] uppercase text-neutral-500">{column.label}</p>
            <div className="text-sm leading-6 text-neutral-800">{renderValue(row[column.key])}</div>
          </div>
        ))}
      </div>

      <CommandButton className="mt-4">
        <ExternalLink className="size-3.5" />
        Open Detail
      </CommandButton>
    </aside>
  );
}
