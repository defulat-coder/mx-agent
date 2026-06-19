import { MetricsGrid } from "@/components/agentos/metrics-grid";
import { getMetrics } from "@/lib/agentos-api";

export default async function LocalMetricsPage() {
  const metrics = await getMetrics();

  return <MetricsGrid data={metrics} gated={false} />;
}
