# Frontend

Frontend application for MX Agent.

## Stack

- Next.js App Router
- React
- TypeScript
- Tailwind CSS v4
- shadcn/ui
- pnpm

## Development

Start the development server:

```bash
pnpm dev
```

Run checks:

```bash
pnpm lint
pnpm build
```

Add shadcn/ui components:

```bash
pnpm dlx shadcn@latest add <component>
```

## Project Layout

- `src/app`: Next.js routes and layouts
- `src/components/ui`: shadcn/ui components
- `src/lib`: shared frontend utilities

## Backend API

The backend API lives in `../backend`. Add frontend environment variables in this
directory when API integration starts, for example:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```
