# Use an official lightweight Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for compiling cryptographic libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install the exact cryptographic library needed for the honeypot
RUN pip install --no-cache-dir paramiko

# Copy the honeypot script and the host key into the container
COPY honeypot.py /app/
COPY server.key /app/

# Expose the honeypot's listening port to the container network
EXPOSE 2222

# Run the honeypot engine when the container launches
CMD ["python", "honeypot.py"]