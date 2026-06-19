import { MemoryPanel } from "@/components/agentos/memory-panel";
import { getTable } from "@/lib/agentos-api";

export default async function MemoryPage() {
  const table = await getTable("memory");
  return <MemoryPanel table={table} />;
}
