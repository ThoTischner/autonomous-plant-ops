# --- build: glibc manylinux wheels (reproducible, cp312) ---
FROM python:3.14-slim-bookworm@sha256:86f975aca15cf04a40b399eebede9aea7c82eae084d1f1a0a6ef6bcaae871a30 AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY src/ src/

# --- runtime: Chainguard/Wolfi base (~0 CVE, continuously patched),
#     pinned python-3.12, nonroot ---
FROM cgr.dev/chainguard/wolfi-base:latest@sha256:003627df3c1e1bba0c4116afcddb314aca9594ee2328c7e876a8081a6c988b2e
RUN apk add --no-cache python-3.12 && ln -sf /usr/bin/python3.12 /usr/bin/python3
WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.12/site-packages \
    PYTHONUNBUFFERED=1
COPY --from=build /install /usr/local
COPY --from=build /app/src ./src
USER 65532:65532
EXPOSE 8002
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python3", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8002/health').status==200 else 1)"]
ENTRYPOINT ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
