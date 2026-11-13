# --- build: glibc manylinux wheels (reproducible, cp312) ---
FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY src/ src/

# --- runtime: Chainguard/Wolfi base (~0 CVE, continuously patched),
#     pinned python-3.12, nonroot ---
FROM cgr.dev/chainguard/wolfi-base:latest@sha256:ae9575b121f5776e2f04e192064bc2c5665af9d1c425d620dc773aca31698712
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
