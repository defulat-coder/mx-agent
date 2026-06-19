# syntax=docker/dockerfile:1.7

FROM node:24-bookworm-slim AS deps
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM node:24-bookworm-slim AS builder
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_AGENTOS_API_BASE_URL=http://localhost:8000
ARG NEXT_PUBLIC_AGENTOS_API_TOKEN=
ENV NEXT_PUBLIC_AGENTOS_API_BASE_URL=$NEXT_PUBLIC_AGENTOS_API_BASE_URL
ENV NEXT_PUBLIC_AGENTOS_API_TOKEN=$NEXT_PUBLIC_AGENTOS_API_TOKEN
RUN pnpm build

FROM node:24-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
