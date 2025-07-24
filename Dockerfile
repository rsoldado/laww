# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
	apt-get install -y --no-install-recommends \
	git pkg-config libffi-dev python3-venv python3-dev build-essential libtool wget && \
	rm -rf /var/lib/apt/lists/*

# Install Zeronet
RUN wget https://github.com/zeronet-conservancy/zeronet-conservancy/archive/refs/tags/v0.7.10.tar.gz && \
	tar -xzf v0.7.10.tar.gz && \
	mkdir -p /app/zeronet && \
	mv zeronet-conservancy-0.7.10/* /app/zeronet/ && \
	rm -rf v0.7.10.tar.gz zeronet-conservancy-0.7.10

WORKDIR /app/zeronet
RUN pip install --upgrade pip && \
	pip install -r requirements.txt

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY laww.py .

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Create needed directories
RUN mkdir -p downloads logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
# Zeronet proxy
EXPOSE 43110
# Web interface
EXPOSE 8080	

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]