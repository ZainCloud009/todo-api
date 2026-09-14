# Use lightweight official Python slim base image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging for container logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set working directory inside container
WORKDIR /app

# Create a non-root system user and group for security best practices
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# Leverage Docker layer caching: install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY main.py .

# Ensure ownership belongs to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Container healthcheck using Python's standard library (no extra packages needed)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# Launch FastAPI using Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
