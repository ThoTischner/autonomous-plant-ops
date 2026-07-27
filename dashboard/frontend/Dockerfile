FROM node:26-alpine@sha256:e88a35be04478413b7c71c455cd9865de9b9360e1f43456be5951032d7ac1a66 AS build
WORKDIR /app
# Use the lockfile so the pinned/overridden (secure) deps are honored.
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Chainguard/Wolfi nginx — distroless, nonroot, continuously rebuilt: ~0 CVEs.
# Serves on unprivileged port 8080 (see nginx.conf).
FROM cgr.dev/chainguard/nginx:latest@sha256:e4ff957080737c90a9ecfeaa40e3d19ea9d687e9cacda2f2a031c75ffcdd72b7
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Chainguard nginx already runs as this nonroot uid; declare it explicitly.
USER 65532
EXPOSE 8080
