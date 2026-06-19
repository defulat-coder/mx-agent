import { DataTable } from "@/components/agentos/data-table";
import { getTable } from "@/lib/agentos-api";

export default async function SchedulerPage() {
  const table = await getTable("schedules");
  return <DataTable table={table} />;
}
