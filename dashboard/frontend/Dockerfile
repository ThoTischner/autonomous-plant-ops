FROM node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609372293 AS build
WORKDIR /app
# Use the lockfile so the pinned/overridden (secure) deps are honored.
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Chainguard/Wolfi nginx — distroless, nonroot, continuously rebuilt: ~0 CVEs.
# Serves on unprivileged port 8080 (see nginx.conf).
FROM cgr.dev/chainguard/nginx@sha256:b66791d04723935f4c3fa436bc6c445eecece8b5136490b7dc976b4555d74fa9
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Chainguard nginx already runs as this nonroot uid; declare it explicitly.
USER 65532
EXPOSE 8080
