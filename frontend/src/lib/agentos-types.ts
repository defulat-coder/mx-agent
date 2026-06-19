export type WorkspaceStatus = "active" | "inactive";

export type NavigationItem = {
  label: string;
  href: string;
  icon: string;
  group: string;
};

export type WorkspaceOverview = {
  workspace: {
    id: string;
    name: string;
    status: WorkspaceStatus;
    plan: string;
    endpoint_url: string;
  };
  user: {
    name: string;
    initials: string;
    email: string;
  };
  navigation: NavigationItem[];
};

export type EntityKind = "agent" | "team" | "workflow" | "interface" | "os";

export type EntityCardData = {
  id: string;
  name: string;
  kind: EntityKind;
  description: string;
  tags: string[];
  stats: string[];
  actions: string[];
};

export type EntitiesResponse = {
  agents: EntityCardData[];
  teams: EntityCardData[];
  workflows: EntityCardData[];
  interfaces: EntityCardData[];
  operating_systems: EntityCardData[];
};

export type TableColumn = {
  key: string;
  label: string;
  mono: boolean;
};

export type TableResponse = {
  title: string;
  database: string;
  table: string;
  columns: TableColumn[];
  rows: Record<string, unknown>[];
  filters: string[];
};

export type MetricsResponse = {
  period: string;
  metrics: Array<{
    label: string;
    value: string;
    points: Array<{ label: string; value: number }>;
  }>;
  model_runs: Array<Record<string, string | number>>;
  gated_message: string | null;
};

export type SettingsResponse = {
  profile: Record<string, string>;
  organization: Record<string, string | number>;
  os: Record<string, unknown>;
  billing: Record<string, unknown>;
};

export type ChatResponse = {
  reply: string;
  action: string | null;
  session_id: string | null;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};
