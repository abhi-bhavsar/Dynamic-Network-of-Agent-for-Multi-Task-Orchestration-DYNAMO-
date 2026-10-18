# ── Stage 1: Build the React Application ─────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json* ./

# Install dependencies cleanly
RUN npm ci || npm install

# Copy frontend source files
COPY . .

# Build production bundle
RUN npm run build

# ── Stage 2: Serve with High-Performance Nginx ──────────────────
FROM nginx:1.25-alpine

# Remove default nginx html
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]