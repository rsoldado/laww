#!/bin/bash
set -e

# Function to cleanup background processes on exit
cleanup() {
	echo "Shutting down services..."
	kill $(jobs -p) 2>/dev/null || true
	exit 0
}
# Set trap for graceful shutdown
trap cleanup EXIT INT TERM QUIT

# Set directories
LOG_DIR="/app/logs"

# Start Zeronet in the background
echo "Starting Zeronet..."
cd /app/zeronet

# Start Zeronet directly
python zeronet.py --ui_ip 0.0.0.0 >> "$LOG_DIR/zeronet.log" 2>&1 &
ZERONET_PID=$!
echo "Waiting for Zeronet to initialize..."
sleep 10

# Start the app
echo "Starting LAWW..."
cd /app
python laww.py 2>&1 | tee -a "$LOG_DIR/laww.log"
