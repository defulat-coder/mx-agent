import { ChevronUp } from "lucide-react";

import { EntityCard } from "@/components/agentos/entity-card";
import { getEntities } from "@/lib/agentos-api";
import type { EntityCardData } from "@/lib/agentos-types";

function EntitySection({
  countLabel,
  entities,
  title,
}: {
  countLabel?: string;
  entities: EntityCardData[];
  title: string;
}) {
  return (
    <section className="mb-8">
      <div className="mb-6 flex items-center gap-2">
        <ChevronUp className="size-4" />
        <h2 className="font-mono text-[12px] uppercase">{title}</h2>
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        {entities.map((entity) => (
          <EntityCard entity={entity} key={entity.id} />
        ))}
      </div>
      {countLabel ? (
        <button className="mt-4 rounded-md bg-neutral-100 px-3 py-2 font-mono text-[11px] uppercase" type="button">
          Show More {countLabel}
        </button>
      ) : null}
    </section>
  );
}

export default async function Home() {
  const entities = await getEntities();

  return (
    <div className="agno-scrollbar min-h-0 flex-1 overflow-auto px-5 py-6">
      <EntitySection countLabel="(+2)" entities={entities.agents} title="Agents" />
      <EntitySection entities={entities.teams} title="Teams" />
      <EntitySection entities={entities.workflows} title="Workflows" />
      <EntitySection entities={entities.interfaces} title="Interfaces" />
      <EntitySection entities={entities.operating_systems} title="Operating Systems" />
    </div>
  );
}
