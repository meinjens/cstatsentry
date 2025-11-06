# Build stage
FROM node:24-alpine AS builder

# Enable corepack for pnpm
RUN corepack enable && corepack prepare pnpm@10.20.0 --activate

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./
COPY prisma ./prisma/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Generate Prisma Client
RUN pnpm prisma:generate

# Production stage
FROM node:24-alpine

# Enable corepack for pnpm
RUN corepack enable && corepack prepare pnpm@10.20.0 --activate

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install production dependencies only
RUN pnpm install --frozen-lockfile --prod

# Copy generated Prisma Client from builder
COPY --from=builder /app/node_modules/.pnpm/@prisma+client* /app/node_modules/.pnpm/
COPY --from=builder /app/node_modules/@prisma /app/node_modules/@prisma

# Copy source code
COPY src ./src
COPY prisma ./prisma

# Create demos directory
RUN mkdir -p /app/demos

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the application
CMD ["pnpm", "start"]
