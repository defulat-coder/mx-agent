import { KnowledgePanel } from "@/components/agentos/knowledge-panel";
import { getTable } from "@/lib/agentos-api";

export default async function KnowledgePage() {
  const table = await getTable("knowledge");
  return <KnowledgePanel table={table} />;
}
