# Use Python slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies including timezone data
RUN apt-get update && apt-get install -y \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (It reads pyproject.toml and uv.lock for dependencies with versions)
RUN uv sync --frozen --no-dev

# Copy all Python application files
COPY *.py ./

# Create directory for analysis files
RUN mkdir -p /app/outputs

# Create data directory for config files
RUN mkdir -p /app/data

# Expose Gradio port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Run the application
CMD ["uv", "run", "app.py"]
