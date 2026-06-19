import { CheckSquare } from "lucide-react";

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
  return (
    <div className="flex min-h-0 flex-1 flex-col px-5 py-5">
      <div className="mb-8 flex items-start justify-between">
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
        <CommandButton className="h-9 justify-between px-4 normal-case">
          <span>{table.filters[0] ?? "View: All"}</span>
          <span className="ml-16 text-[9px]">▼</span>
        </CommandButton>
      </div>

      <div className="min-h-0 flex-1 overflow-auto">
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
            {table.rows.map((row, index) => (
              <tr className="border-b border-neutral-100 text-neutral-700" key={String(row.id ?? index)}>
                <td className="px-4 py-4">
                  <span className="block size-4 rounded border border-neutral-300" />
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
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
