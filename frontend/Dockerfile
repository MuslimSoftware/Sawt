# ---------- Stage 1 : build the Next.js app ----------
FROM node:20-alpine AS builder

# Install tini (PID 1) & git for post-install hooks that need it
RUN apk add --no-cache tini git

WORKDIR /app

# Faster installs using npm ci when package-lock.json exists
COPY package*.json ./
RUN npm ci --legacy-peer-deps

# Copy the rest of the source and build
COPY . .
RUN npm run build

# ---------- Stage 2 : slim runtime image ----------
FROM node:20-alpine AS runner

# tini = proper signal handling in containers
RUN apk add --no-cache tini

ENV NODE_ENV=production
WORKDIR /app

# Only what we need at runtime
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

# If you export static assets (next export) add: COPY --from=builder /app/out ./out

EXPOSE 3000
ENTRYPOINT ["/sbin/tini","--"]
CMD ["npm","start"]    # uses "next start" under the hood
