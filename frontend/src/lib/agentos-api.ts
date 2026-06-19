import {
  fallbackEntities,
  fallbackMetrics,
  fallbackOverview,
  fallbackSettings,
  fallbackTables,
} from "@/lib/agentos-data";
import type {
  ChatResponse,
  EntitiesResponse,
  MetricsResponse,
  SettingsResponse,
  TableResponse,
  WorkspaceOverview,
} from "@/lib/agentos-types";

const apiBase = process.env.NEXT_PUBLIC_AGENTOS_API_BASE_URL;
const apiToken = process.env.NEXT_PUBLIC_AGENTOS_API_TOKEN;

async function getJson<T>(path: string, fallback: T): Promise<T> {
  if (!apiBase) {
    return fallback;
  }

  try {
    const response = await fetch(`${apiBase}${path}`, {
      cache: "no-store",
      headers: apiToken ? { Authorization: `Bearer ${apiToken}` } : {},
    });

    if (!response.ok) {
      return fallback;
    }

    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export function getOverview(): Promise<WorkspaceOverview> {
  return getJson("/v1/os/overview", fallbackOverview);
}

export function getEntities(): Promise<EntitiesResponse> {
  return getJson("/v1/os/entities", fallbackEntities);
}

export function getTable(kind: keyof typeof fallbackTables): Promise<TableResponse> {
  const endpoint = kind === "evaluations" ? "/v1/os/evaluations" : `/v1/os/${kind}`;
  return getJson(endpoint, fallbackTables[kind]);
}

export function getMetrics(): Promise<MetricsResponse> {
  return getJson("/v1/os/metrics", fallbackMetrics);
}

export function getSettings(): Promise<SettingsResponse> {
  return getJson("/v1/os/settings", fallbackSettings);
}

export async function sendChatMessage(message: string, sessionId?: string): Promise<ChatResponse> {
  if (!apiBase) {
    const previewReply = /agno/i.test(message)
      ? "Agno is a lightweight Python framework for building AI agents with models, tools, knowledge, workflows, memory, and deployment/monitoring via AgentOS."
      : "MX AgentOS is running in local preview mode. Connect NEXT_PUBLIC_AGENTOS_API_BASE_URL and NEXT_PUBLIC_AGENTOS_API_TOKEN to chat with the backend.";

    return {
      reply: previewReply,
      action: null,
      session_id: sessionId ?? "preview-session",
    };
  }

  const response = await fetch(`${apiBase}/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(apiToken ? { Authorization: `Bearer ${apiToken}` } : {}),
    },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed with ${response.status}`);
  }

  return (await response.json()) as ChatResponse;
}
