"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const items = [
  ["Profile", "/settings/profile"],
  ["Organization", "/settings/organization"],
  ["OS", "/settings/os"],
  ["Roles", "/settings/roles"],
  ["Billing", "/settings/billing"],
] as const;

export function SettingsNav() {
  const pathname = usePathname();

  return (
    <div className="mb-6 flex flex-wrap gap-2">
      {items.map(([label, href]) => (
        <Link
          className={cn(
            "rounded-md border border-neutral-200 px-3 py-2 font-mono text-[11px] uppercase",
            pathname === href ? "bg-neutral-950 text-white" : "bg-neutral-50 text-neutral-800",
          )}
          href={href}
          key={href}
        >
          {label}
        </Link>
      ))}
    </div>
  );
}
