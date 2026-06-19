import { DataTable } from "@/components/agentos/data-table";
import { getTable } from "@/lib/agentos-api";

export default async function MemoryPage() {
  const table = await getTable("memory");
  return <DataTable table={table} />;
}
