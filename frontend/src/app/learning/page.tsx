import { StatusState } from "@/components/agentos/status-state";

export default function LearningPage() {
  return (
    <div className="relative min-h-0 flex-1">
      <StatusState
        description="Learning runs, feedback, and improvement jobs will connect to eval and memory pipelines in later phases."
        title="Learning queue is empty"
      />
    </div>
  );
}
