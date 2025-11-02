# Multi-stage build for CAD-P bot with GDAL support

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libgdal-dev \
    gdal-bin \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    # Install GDAL Python bindings matching system GDAL version
    GDAL_VERSION=$(gdal-config --version) && \
    pip install GDAL==${GDAL_VERSION}

# Stage 2: Runtime stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    GDAL_DATA=/usr/share/gdal

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal32 \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create application user
RUN useradd -m -u 1000 botuser && \
    mkdir -p /app /app/logs /app/temp /app/output /app/data /app/templates && \
    chown -R botuser:botuser /app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=botuser:botuser src/ /app/src/
COPY --chown=botuser:botuser pyproject.toml /app/
COPY --chown=botuser:botuser README.md /app/

# Copy templates and examples if they exist
COPY --chown=botuser:botuser templates/ /app/templates/ 2>/dev/null || :
COPY --chown=botuser:botuser examples/ /app/examples/ 2>/dev/null || :

# Switch to non-root user
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "cad_p"]
