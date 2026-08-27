FROM python:3.12-slim@sha256:7a8b475003c4fe15a2cd4e55e5cfc2f3560bdc9333d624f24cdd6d4340fd7a17
WORKDIR /app
RUN pip install --no-cache-dir pytest httpx
COPY integration/ integration/
CMD ["pytest", "integration/", "-v"]
