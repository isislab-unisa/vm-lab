# syntax=docker/dockerfile:1
# PARTIALLY GENERATED with docker init
# Help with streamlit and docker: https://docs.streamlit.io/deploy/tutorials/docker

FROM python:3.12.9-slim

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install necessary packages and delete apt-get cache.
# - curl: for healthcheck
# - openssl: for generating keys
RUN apt-get update && apt-get install -y \
    curl \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY . .

# Create the streamlit secrets file.
RUN mv template_secrets.toml .streamlit/secrets.toml

# Generate random keys for secrets.toml
RUN export COOKIE_KEY=$(openssl rand -base64 32) && sed -i "s|some cookie key|$COOKIE_KEY|g" .streamlit/secrets.toml
RUN export FERNET_KEY=$(openssl rand -base64 32) && sed -i "s|some Fernet compliant key|$FERNET_KEY|g" .streamlit/secrets.toml

# Expose the port that the application listens on.
EXPOSE 8501

# Healthcheck to ensure the application is running.
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application.
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]