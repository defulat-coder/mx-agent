import { ApprovalsList } from "@/components/agentos/approvals-list";
import { getTable } from "@/lib/agentos-api";

type ApprovalStatus = "all" | "pending" | "approved" | "rejected";

function normalizeStatus(value: string | string[] | undefined): ApprovalStatus {
  const status = Array.isArray(value) ? value[0] : value;
  if (status === "pending" || status === "approved" || status === "rejected" || status === "all") {
    return status;
  }

  return "all";
}

export default async function ApprovalsPage({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = (await searchParams) ?? {};
  const table = await getTable("approvals");

  return <ApprovalsList initialStatus={normalizeStatus(params.status)} table={table} />;
}
