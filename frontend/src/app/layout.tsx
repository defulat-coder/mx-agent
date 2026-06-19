import type { Metadata } from "next";

import { AppShell } from "@/components/agentos/app-shell";
import { getOverview } from "@/lib/agentos-api";

import "./globals.css";

export const metadata: Metadata = {
  title: "MX AgentOS",
  description: "Production console for MX Agent",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const overview = await getOverview();

  return (
    <html
      lang="en"
      className="h-full antialiased"
    >
      <body className="min-h-full">
        <AppShell
          navigation={overview.navigation}
          userInitials={overview.user.initials}
          workspaceName={overview.workspace.name}
        >
          {children}
        </AppShell>
      </body>
    </html>
  );
}
