# Multi-stage Dockerfile for CE Demo Backend API
# Optimized for production with security, performance, and size considerations
#
# Features:
# - Multi-stage build to minimize final image size
# - Poetry for dependency management
# - Non-root user for security
# - Build cache optimization
# - Health checks and monitoring
# - Security scanning friendly

# =============================================================================
# Build Stage: Dependencies and compilation
# =============================================================================
FROM python:3.11-slim as builder

# Build arguments
ARG POETRY_VERSION=1.7.1
ARG BUILDKIT_INLINE_CACHE=1

# Set environment variables for reproducible builds
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    # Compilation tools
    gcc \
    g++ \
    make \
    cmake \
    # Database drivers
    libpq-dev \
    # Additional libraries for ML/Data processing
    libffi-dev \
    libssl-dev \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Poetry
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

# Set working directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root --no-dev \
    && rm -rf $POETRY_CACHE_DIR

# =============================================================================
# Runtime Stage: Minimal production image
# =============================================================================

FROM python:3.11-slim as runtime

# Runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Security
    PYTHONHASHSEED=random \
    # Performance
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Application
    APP_HOME=/app \
    APP_USER=appuser \
    APP_UID=1000 \
    APP_GID=1000

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    # Runtime libraries
    libpq5 \
    # Health check and monitoring
    curl \
    dumb-init \
    # Timezone data
    tzdata \
    # SSL certificates
    ca-certificates \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    # Remove unnecessary packages
    && apt-get autoremove -y

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create application directory and user
RUN groupadd -g $APP_GID $APP_USER \
    && useradd -m -u $APP_UID -g $APP_GID -s /bin/bash $APP_USER \
    && mkdir -p $APP_HOME \
    && chown -R $APP_USER:$APP_USER $APP_HOME

# Set working directory
WORKDIR $APP_HOME

# Copy application code with proper ownership
COPY --chown=$APP_USER:$APP_USER src/ ./src/
COPY --chown=$APP_USER:$APP_USER scripts/ ./scripts/
COPY --chown=$APP_USER:$APP_USER alembic.ini ./
COPY --chown=$APP_USER:$APP_USER docker/entrypoint.sh ./

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER $APP_USER

# Create necessary directories
RUN mkdir -p logs data temp

# Expose application port
EXPOSE 8000

# Add labels for metadata
LABEL org.opencontainers.image.title="CE Demo Backend API" \
      org.opencontainers.image.description="Sistema de Matching Inteligente para Estágios" \
      org.opencontainers.image.vendor="Companhia de Estágios" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.created="2025-07-24" \
      org.opencontainers.image.source="https://github.com/ce-demo/ce-demo" \
      org.opencontainers.image.licenses="Proprietary"

# Health check with comprehensive validation
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=40s \
            --retries=3 \
            CMD curl -f http://localhost:8000/health \
                && curl -f http://localhost:8000/api/v1/system/health \
                || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Default command - can be overridden
CMD ["./entrypoint.sh"]