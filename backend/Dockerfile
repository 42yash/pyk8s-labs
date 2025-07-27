# Use a specific Python version (Debian-based)
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Add a build argument for the Docker GID, defaulting to a common value
ARG DOCKER_GID=999

# Install essential dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# --- FINAL CORRECTED USER/GROUP SETUP ---
# Add build arguments for UID and GID
ARG UID=1000
ARG GID=1000

# Create a system group 'docker' with the specified GID from the host.
RUN addgroup --system --gid ${DOCKER_GID} docker

# Create a non-root system user 'app' with the specified UID from the host
# AND its corresponding group 'app'. This ensures it matches the host user.
RUN adduser --system --no-create-home --uid ${UID} --group app

# Add the 'app' user to the 'docker' group.
RUN adduser app docker
# --- END USER/GROUP SETUP ---

# --- CORRECTED ARCHITECTURE-AWARE KinD INSTALL ---
# Use TARGETARCH to download the correct binary for the build architecture (amd64 vs arm64)
ARG TARGETARCH
RUN case ${TARGETARCH} in \
         "amd64") ARCH="amd64" ;; \
         "arm64") ARCH="arm64" ;; \
         *) echo "Unsupported architecture: ${TARGETARCH}"; exit 1 ;; \
    esac && \
    curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-${ARCH}

RUN chmod +x ./kind
RUN mv ./kind /usr/local/bin/kind
# --- END KinD INSTALL ---

# Install Docker Client (This is already architecture-aware)
RUN curl -L https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz | tar -xz
RUN mv docker/docker /usr/local/bin/docker
RUN rm -rf docker

# Copy dependency file first for layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY . .

# Change ownership to the new non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
