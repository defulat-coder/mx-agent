import { LocalSchedulerPanel } from "@/components/agentos/scheduler-panel";
import { getTable } from "@/lib/agentos-api";

export default async function LocalSchedulerPage() {
  const table = await getTable("schedules");

  return <LocalSchedulerPanel table={table} />;
}
