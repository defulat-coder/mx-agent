import { SchedulerPanel } from "@/components/agentos/scheduler-panel";
import { getTable } from "@/lib/agentos-api";

export default async function SchedulerPage() {
  const table = await getTable("schedules");
  return <SchedulerPanel table={table} />;
}
