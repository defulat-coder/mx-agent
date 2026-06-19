import { DataTable } from "@/components/agentos/data-table";
import { getTable } from "@/lib/agentos-api";

export default async function SessionsPage() {
  const table = await getTable("sessions");
  return <DataTable table={table} />;
}
