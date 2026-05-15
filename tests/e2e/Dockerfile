FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy
WORKDIR /app
RUN pip install --no-cache-dir pytest==8.3.4 playwright==1.49.0
COPY . /app/e2e/
CMD ["pytest", "e2e/", "-v", "--tb=short"]
