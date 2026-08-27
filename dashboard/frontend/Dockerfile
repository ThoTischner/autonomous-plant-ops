FROM node:26-alpine@sha256:bff25b16ab13b4789c8d78489c249239fb74c85319cc90fc6122c40123894f1e AS build
WORKDIR /app
# Use the lockfile so the pinned/overridden (secure) deps are honored.
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Chainguard/Wolfi nginx — distroless, nonroot, continuously rebuilt: ~0 CVEs.
# Serves on unprivileged port 8080 (see nginx.conf).
FROM cgr.dev/chainguard/nginx:latest@sha256:38e202d0304b7bf0235ade6ef622c8bf0242fdd5c674bf301ca5cbbb378ff7df
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Chainguard nginx already runs as this nonroot uid; declare it explicitly.
USER 65532
EXPOSE 8080
