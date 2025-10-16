# This is a Dockerfile for LiveKit Voice Agent with MCP Toolbox
# Based on LiveKit's official custom deployment example
# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Install gcc and other build dependencies.
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

USER appuser

RUN mkdir -p /home/appuser/.cache
RUN chown -R appuser /home/appuser/.cache

WORKDIR /home/appuser

COPY requirements.txt .
RUN python -m pip install --user --no-cache-dir -r requirements.txt

COPY . .

# Create the volunteer database at build time
RUN python create_volunteers_db.py

# ensure that any dependent models are downloaded at build-time
RUN python agent.py download-files || echo "download-files command not available, skipping model pre-download"

# expose healthcheck port
EXPOSE 8081

# Run the application.
CMD ["python", "agent.py", "start"]