import { HomePanel } from "@/components/agentos/home-panel";
import { getEntities } from "@/lib/agentos-api";

export default async function Home() {
  const entities = await getEntities();

  return (
    <HomePanel
      sections={{
        agents: entities.agents,
        teams: entities.teams,
        workflows: entities.workflows,
      }}
    />
  );
}
