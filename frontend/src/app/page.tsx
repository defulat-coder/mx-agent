import { ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="flex min-h-svh items-center justify-center bg-background px-6 py-16">
      <section className="w-full max-w-2xl">
        <p className="mb-3 text-sm font-medium text-muted-foreground">
          MX Agent
        </p>
        <h1 className="text-4xl font-semibold tracking-normal text-foreground sm:text-5xl">
          Frontend scaffold is ready.
        </h1>
        <p className="mt-5 max-w-xl text-base leading-7 text-muted-foreground">
          This app is configured with Next.js, React, TypeScript, Tailwind CSS,
          shadcn/ui, and pnpm.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button>
            Start building
            <ArrowRight />
          </Button>
          <Button variant="outline">View docs</Button>
        </div>
      </section>
    </main>
  );
}
