# Multi-stage Dockerfile for Email Notification Service
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application files
COPY email_notification_service.py .
COPY templates/ ./templates/
COPY run_service.sh .

# Make run script executable
RUN chmod +x run_service.sh

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Add local bin to PATH for user-installed packages
ENV PATH=/root/.local/bin:$PATH

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import email_notification_service; print('Service is healthy')" || exit 1

# Default command
CMD ["./run_service.sh"]