<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Frontend Overview

This subtree contains the Next.js frontend for MX Agent. It uses Next.js 16 App
Router, React 19, TypeScript, Tailwind CSS v4, shadcn/ui, lucide-react, and
pnpm.

## Layout

- `src/app/`: App Router entry files, layouts, pages, and global CSS.
- `src/components/`: reusable React components.
- `src/components/ui/`: shadcn/ui components.
- `src/lib/`: shared frontend utilities.
- `public/`: static assets.
- `components.json`: shadcn/ui configuration.

## Commands

```bash
pnpm install
pnpm dev
pnpm lint
pnpm build
```

Add shadcn/ui components:

```bash
pnpm dlx shadcn@latest add <component>
```

## Guidance

- Use `pnpm` for dependency operations. Do not add npm or yarn lockfiles.
- Prefer shadcn/ui components, `lucide-react` icons, and local utilities from
  `@/components` and `@/lib` over one-off primitives.
- Keep App Router files under `src/app/`, reusable UI under `src/components/`,
  and shared helpers under `src/lib/`.
- Before editing framework-sensitive code, read the relevant installed Next.js
  documentation under `node_modules/next/dist/docs/`.
- Do not commit generated output such as `.next/`, `out/`, coverage, or
  `next-env.d.ts`.

## Testing

- Run `pnpm lint` for frontend code changes.
- Run `pnpm build` when changes affect routing, rendering, imports, config, or
  integration behavior.
