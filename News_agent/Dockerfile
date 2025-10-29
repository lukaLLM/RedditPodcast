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

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY config.py \
     utils.py \
     reddit_fetcher.py \
     ai_analyzer.py \
     telegram_sender.py \
     scheduler.py \
     workflow.py \
     app.py ./

# Create non-root user with same UID as host user (1000 is typical)
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Create directories with correct permissions
RUN mkdir -p /app/outputs /app/data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Gradio port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Run the application
CMD ["uv", "run", "app.py"]