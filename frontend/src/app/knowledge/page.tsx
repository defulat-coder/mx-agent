import { DataTable } from "@/components/agentos/data-table";
import { getTable } from "@/lib/agentos-api";

export default async function KnowledgePage() {
  const table = await getTable("knowledge");
  return <DataTable table={table} />;
}
