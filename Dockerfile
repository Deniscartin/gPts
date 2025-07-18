# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (multi-architecture support)
RUN if [ "$(uname -m)" = "x86_64" ]; then \
        # AMD64 architecture
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
        && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
        && apt-get update \
        && apt-get install -y google-chrome-stable; \
    elif [ "$(uname -m)" = "aarch64" ]; then \
        # ARM64 architecture - use Chromium instead
        apt-get update \
        && apt-get install -y chromium \
        && ln -s /usr/bin/chromium /usr/bin/google-chrome; \
    else \
        # Fallback for other architectures
        apt-get update \
        && apt-get install -y chromium \
        && ln -s /usr/bin/chromium /usr/bin/google-chrome; \
    fi \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for Chrome user data
RUN mkdir -p /app/chrome-data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/ || exit 1

# Start command
CMD ["python", "data_server.py"] 