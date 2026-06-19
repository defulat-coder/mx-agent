import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { AppShell } from "@/components/agentos/app-shell";
import { getOverview } from "@/lib/agentos-api";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

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
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
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
