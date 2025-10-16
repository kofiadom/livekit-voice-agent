# Dockerfile for LiveKit Voice Agent with MCP Toolbox
# Uses UV for faster, more reliable dependency management
# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Install system dependencies including UV
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Switch to non-privileged user
USER appuser

# Create cache directory
RUN mkdir -p /home/appuser/.cache
RUN chown -R appuser /home/appuser/.cache

WORKDIR /home/appuser

# Copy dependency files first for better Docker layer caching
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Install dependencies using UV (much faster than pip)
RUN /root/.cargo/bin/uv sync --frozen

# Copy application code
COPY --chown=appuser:appuser . .

# Create the volunteer database at build time
RUN /root/.cargo/bin/uv run python create_volunteers_db.py

# Ensure any dependent models are downloaded at build-time
RUN /root/.cargo/bin/uv run python agent.py download-files

# Expose healthcheck port (LiveKit agents typically use 8081)
EXPOSE 8081

# Run the application using UV
CMD ["/root/.cargo/bin/uv", "run", "python", "agent.py", "start"]