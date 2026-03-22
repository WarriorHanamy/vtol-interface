# Minimal Dockerfile for log_streamer service
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY log_streamer/ ./log_streamer/

# Install only required dependencies (fastapi includes httpcore)
RUN pip install --no-cache-dir --user fastapi uvicorn

# Expose port
EXPOSE 8000

# Run as non-root user
RUN useradd -m -u 1000 logstreamer && \
    chown -R logstreamer:logstreamer /app

USER logstreamer

# Add local Python bin to PATH
ENV PATH="/home/logstreamer/.local/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# Run the application
CMD ["uvicorn", "log_streamer.main:app", "--host", "0.0.0.0", "--port", "8000"]
