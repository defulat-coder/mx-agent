import { DataTable } from "@/components/agentos/data-table";
import { getTable } from "@/lib/agentos-api";

export default async function ApprovalsPage() {
  const table = await getTable("approvals");
  return <DataTable table={table} />;
}
