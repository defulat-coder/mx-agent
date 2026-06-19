import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type CommandButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  tone?: "default" | "dark";
};

export function CommandButton({
  children,
  className,
  tone = "default",
  type = "button",
  ...props
}: CommandButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-7 items-center justify-center gap-1.5 rounded-md border px-3 font-mono text-[11px] uppercase tracking-normal transition-colors",
        tone === "dark"
          ? "border-neutral-900 bg-neutral-950 text-white hover:bg-neutral-800"
          : "border-neutral-200 bg-neutral-50 text-neutral-900 hover:bg-neutral-100",
        className,
      )}
      type={type}
      {...props}
    >
      {children}
    </button>
  );
}
