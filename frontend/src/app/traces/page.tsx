import { DataTable } from "@/components/agentos/data-table";
import { getTable } from "@/lib/agentos-api";

export default async function TracesPage() {
  const table = await getTable("traces");
  return <DataTable table={table} />;
}
