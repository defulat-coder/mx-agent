import { EvaluationPanel } from "@/components/agentos/evaluation-panel";
import { getTable } from "@/lib/agentos-api";

export default async function EvaluationPage() {
  const table = await getTable("evaluations");
  return <EvaluationPanel table={table} />;
}
