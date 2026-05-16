# --- build stage: install deps with a normal toolchain ---
FROM python:3.11-slim-bookworm AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY src/ src/

# --- runtime: distroless (no shell, no pkg manager, nonroot) ---
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages \
    PYTHONUNBUFFERED=1
COPY --from=build /install /usr/local
COPY --from=build /app/src ./src
CMD ["-u", "src/main.py"]
