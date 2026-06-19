import { DataTable } from "@/components/agentos/data-table";
import { getTable } from "@/lib/agentos-api";

export default async function EvaluationPage() {
  const table = await getTable("evaluations");
  return <DataTable table={table} />;
}
