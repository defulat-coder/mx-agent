import { TraceExplorer } from "@/components/agentos/trace-explorer";
import { getTable } from "@/lib/agentos-api";

export default async function TracesPage() {
  const table = await getTable("traces");
  return <TraceExplorer table={table} />;
}
