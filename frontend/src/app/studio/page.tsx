import { StatusState } from "@/components/agentos/status-state";

export default function StudioPage() {
  return (
    <div className="relative min-h-0 flex-1">
      <StatusState
        description="Studio surfaces editable agent, team, and workflow configuration in the next phase."
        title="Studio is ready for configuration"
      />
    </div>
  );
}
