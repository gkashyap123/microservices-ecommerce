# ════════════════════════════════════════════════════════════════════════════
# Build stage
# ════════════════════════════════════════════════════════════════════════════
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including devDependencies for build)
RUN npm ci --include=dev

# Copy source code
COPY . .

# Build the application with detailed output
RUN echo "Starting TypeScript compilation and Vite build..." && \
    npm run build 2>&1

# ════════════════════════════════════════════════════════════════════════════
# Runtime stage
# ════════════════════════════════════════════════════════════════════════════
FROM node:18-alpine

WORKDIR /app

# Install serve to run the built app
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD wget --quiet --tries=1 --spider http://localhost:5173/ || exit 1

# Start the application
CMD ["serve", "-s", "dist", "-l", "5173"]
