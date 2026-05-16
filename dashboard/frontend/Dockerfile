FROM node:20-alpine AS build
WORKDIR /app
# Use the lockfile so the pinned/overridden (secure) deps are honored.
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Chainguard/Wolfi nginx — distroless, nonroot, continuously rebuilt: ~0 CVEs.
# Serves on unprivileged port 8080 (see nginx.conf).
FROM cgr.dev/chainguard/nginx:latest
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
