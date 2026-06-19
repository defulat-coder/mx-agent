import { StudioPanel } from "@/components/agentos/studio-panel";
import { getEntities } from "@/lib/agentos-api";

export default async function StudioPage() {
  const entities = await getEntities();
  return <StudioPanel agents={entities.agents} />;
}
