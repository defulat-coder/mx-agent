"use client";

import {
  BarChart3,
  BookOpen,
  Bot,
  Brain,
  CalendarClock,
  ChevronDown,
  ClipboardCheck,
  Database,
  Gamepad2,
  Globe2,
  Home,
  LayoutGrid,
  ListTree,
  Mail,
  MessageSquare,
  MoreVertical,
  PanelLeft,
  Play,
  RefreshCw,
  Settings,
  SquareCheck,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentType, ReactNode } from "react";

import { CommandButton } from "@/components/agentos/command-button";
import { cn } from "@/lib/utils";

const iconMap: Record<string, ComponentType<{ className?: string }>> = {
  home: Home,
  "message-square": MessageSquare,
  play: Play,
  "list-tree": ListTree,
  "layout-grid": LayoutGrid,
  brain: Brain,
  database: Database,
  "book-open": BookOpen,
  "chart-no-axes-column": BarChart3,
  "clipboard-check": ClipboardCheck,
  "square-check": SquareCheck,
  "calendar-clock": CalendarClock,
  settings: Settings,
};

type ShellItem = {
  label: string;
  href: string;
  icon: string;
  group: string;
};

export function AppShell({
  children,
  navigation,
  workspaceName,
  userInitials,
}: {
  children: ReactNode;
  navigation: ShellItem[];
  workspaceName: string;
  userInitials: string;
}) {
  const pathname = usePathname();
  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);

  return (
    <div className="min-h-svh bg-[#f4f4f5] text-neutral-950">
      <div className="flex h-10 items-center justify-between bg-[#777780] px-4 text-sm text-white">
        <p>You are using MX AgentOS local preview. Production data stays in your deployment.</p>
        <div className="flex items-center gap-2">
          <CommandButton className="h-6 border-neutral-950 bg-neutral-950 text-white">
            What is Demo OS?
          </CommandButton>
          <CommandButton className="h-6 border-white/40 bg-white text-neutral-900">
            Leave Demo OS
          </CommandButton>
        </div>
      </div>

      <div className="flex h-[calc(100svh-40px)]">
        <aside className="flex w-52 shrink-0 flex-col border-r border-neutral-200 bg-[#f2f2f3]">
          <div className="flex h-16 items-center justify-between px-4">
            <Link className="flex items-center gap-2 text-sm font-medium" href="/">
              <span className="grid size-6 place-items-center rounded-md bg-[#ff3b25] text-xs font-bold text-white">
                A
              </span>
              Agno
            </Link>
            <button
              aria-label="Collapse sidebar"
              className="grid size-7 place-items-center rounded-md text-neutral-600 hover:bg-neutral-200"
              type="button"
            >
              <PanelLeft className="size-4" />
            </button>
          </div>

          <nav className="flex-1 space-y-0.5 px-2">
            {navigation.map((item, index) => {
              const Icon = iconMap[item.icon] ?? Home;
              const active = isActive(item.href);
              const hasDivider = index === 1 || item.group === "settings";

              return (
                <div key={item.href}>
                  {hasDivider ? <div className="my-2 border-t border-neutral-200" /> : null}
                  <Link
                    className={cn(
                      "flex h-7 items-center gap-2 rounded-md px-2 text-sm text-neutral-600 transition-colors",
                      active && "bg-white text-[#ff3b25] shadow-[0_1px_0_rgba(0,0,0,0.03)]",
                      !active && "hover:bg-neutral-200/70 hover:text-neutral-900",
                    )}
                    href={item.href}
                  >
                    <Icon className="size-3.5" />
                    <span className="flex-1">{item.label}</span>
                    {["Studio", "Learning", "Settings"].includes(item.label) ? (
                      <ChevronDown className="size-3.5 text-neutral-900" />
                    ) : null}
                  </Link>
                </div>
              );
            })}
          </nav>

          <div className="px-4 py-5">
            <div className="mb-9 flex items-center justify-between text-neutral-500">
              <BookOpen className="size-4" />
              <span className="h-4 border-l border-neutral-300" />
              <Gamepad2 className="size-4" />
              <span className="h-4 border-l border-neutral-300" />
              <Bot className="size-4" />
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="font-mono">{userInitials}</span>
              <span className="font-medium">None None</span>
              <MoreVertical className="ml-auto size-4 text-neutral-500" />
            </div>
          </div>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col p-3 pl-0">
          <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-[0_1px_2px_rgba(0,0,0,0.04)]">
            <header className="flex h-14 shrink-0 items-center justify-between border-b border-neutral-200 px-5">
              <div className="flex items-center gap-3">
                <span className="grid size-7 place-items-center rounded-full border border-neutral-200 bg-white">
                  <Globe2 className="size-4" />
                </span>
                <span className="text-sm font-medium">{workspaceName}</span>
                <span className="size-2 rounded-full bg-emerald-400 shadow-[0_0_0_4px_rgba(52,211,153,0.16)]" />
              </div>
              <div className="flex items-center gap-2">
                <CommandButton>
                  <Mail className="size-3.5" />
                  Get Support
                </CommandButton>
                <CommandButton>
                  <RefreshCw className="size-3.5" />
                  Refresh
                </CommandButton>
              </div>
            </header>
            {children}
          </section>
        </main>
      </div>
    </div>
  );
}
