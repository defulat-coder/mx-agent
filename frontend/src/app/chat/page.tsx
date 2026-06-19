import { ChatSurface } from "@/components/agentos/chat-surface";

type ChatPageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

const typeToGroup = {
  agent: "agents",
  team: "teams",
  workflow: "workflows",
} as const;

function firstParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export default async function ChatPage({ searchParams }: ChatPageProps) {
  const params = await searchParams;
  const type = firstParam(params?.type);
  const group = type && type in typeToGroup ? typeToGroup[type as keyof typeof typeToGroup] : undefined;

  return (
    <ChatSurface
      initialEntityId={firstParam(params?.id)}
      initialGroup={group}
      initialSessionId={firstParam(params?.session)}
    />
  );
}
