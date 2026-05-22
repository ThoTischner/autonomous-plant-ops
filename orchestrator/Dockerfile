# --- build: glibc manylinux wheels (reproducible, cp312) ---
FROM python:3.14-slim-bookworm@sha256:a9bee15510a364124aa24692899d269835683b883de42f7ebec8c293cf679ccb AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY src/ src/

# --- runtime: Chainguard/Wolfi base (~0 CVE, continuously patched),
#     pinned python-3.12, nonroot ---
FROM cgr.dev/chainguard/wolfi-base@sha256:0cff4df29a6597173dc8b813787318150141eb96ac783dc3ff4f5ff52c49a1e2
RUN apk add --no-cache python-3.12 && ln -sf /usr/bin/python3.12 /usr/bin/python3
WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.12/site-packages \
    PYTHONUNBUFFERED=1
COPY --from=build /install /usr/local
COPY --from=build /app/src ./src
USER 65532:65532
ENTRYPOINT ["python3", "-u", "src/main.py"]
