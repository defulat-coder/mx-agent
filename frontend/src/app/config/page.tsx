import { ConfigPanel, MissingConfigPanel } from "@/components/agentos/config-panel";
import { getEntities } from "@/lib/agentos-api";

export default async function ConfigPage({
  searchParams,
}: {
  searchParams: Promise<{ id?: string; type?: string }>;
}) {
  const [{ id, type }, entities] = await Promise.all([searchParams, getEntities()]);
  const candidates = [...entities.agents, ...entities.teams, ...entities.workflows];
  const entity = candidates.find((item) => item.id === id && (!type || item.kind === type));

  if (!entity) {
    return <MissingConfigPanel />;
  }

  return <ConfigPanel entity={entity} />;
}
