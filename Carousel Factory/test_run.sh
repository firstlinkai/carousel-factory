#!/bin/bash
# test_run.sh - Triggers the Carousel Factory End-to-End Pipeline
set -e

# Target URL and Content Topic
TARGET_URL="https://example-agency.com"
TOPIC="Why AI is the future of design workflows"

echo "========================================"
echo "🚀 Starting Carousel Factory Pipeline"
echo "URL: $TARGET_URL"
echo "TOPIC: $TOPIC"
echo "========================================"

# Run the pipeline module
PYTHONPATH="." python3 src/main.py "$TARGET_URL" "$TOPIC"

echo "========================================"
echo "✅ Pipeline script completed."
echo "You can view the final deliverable by opening output/index.html in your browser."
echo "========================================"
