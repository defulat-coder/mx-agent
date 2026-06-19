import { LearningPanel, type LearningSectionId } from "@/components/agentos/learning-panel";

const sections = ["user_memory", "user_profile", "entity_memory", "session_context", "decision_log"] as const;

function normalizeSection(section: string): LearningSectionId {
  return sections.some((item) => item === section) ? (section as LearningSectionId) : "user_memory";
}

export default async function LearningSectionPage({
  params,
}: {
  params: Promise<{ section: string }>;
}) {
  const { section } = await params;
  return <LearningPanel section={normalizeSection(section)} />;
}
