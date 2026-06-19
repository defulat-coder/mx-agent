import { SessionsPanel } from "@/components/agentos/sessions-panel";
import { getTable } from "@/lib/agentos-api";

type SessionKind = "all" | "agent" | "team" | "workflow";

function normalizeType(value: string | string[] | undefined): SessionKind {
  const type = Array.isArray(value) ? value[0] : value;
  if (type === "agent" || type === "team" || type === "workflow" || type === "all") {
    return type;
  }

  return "all";
}

function normalizePage(value: string | string[] | undefined) {
  const page = Number(Array.isArray(value) ? value[0] : value);
  if (!Number.isFinite(page) || page < 1) {
    return 1;
  }

  return Math.floor(page);
}

export default async function SessionsPage({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = (await searchParams) ?? {};
  const table = await getTable("sessions");
  return (
    <SessionsPanel
      initialPage={normalizePage(params.page)}
      initialType={normalizeType(params.type)}
      table={table}
    />
  );
}
