FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy@sha256:70c06141ac9041eedef4a68387ea978ceb090c37bd5b66583353b7fe17b9f3d7
WORKDIR /app
RUN pip install --no-cache-dir pytest==8.3.4 playwright==1.49.0
COPY . /app/e2e/
CMD ["pytest", "e2e/", "-v", "--tb=short"]
