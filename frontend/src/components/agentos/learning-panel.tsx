"use client";

export const learningSections = [
  { id: "user_memory", label: "User Memories" },
  { id: "user_profile", label: "User Profiles" },
  { id: "entity_memory", label: "Entity Memories" },
  { id: "session_context", label: "Session Context" },
  { id: "decision_log", label: "Decision Logs" },
] as const;

export type LearningSectionId = (typeof learningSections)[number]["id"];

export function LearningPanel({ section }: { section: LearningSectionId }) {
  return (
    <div className="grid min-h-0 flex-1 place-items-center">
      <div className="flex items-center gap-1.5" aria-label={`${section} loading`}>
        <span className="size-2 rounded-full bg-neutral-300" />
        <span className="size-2 rounded-full bg-neutral-300" />
        <span className="size-2 rounded-full bg-neutral-300" />
      </div>
    </div>
  );
}
