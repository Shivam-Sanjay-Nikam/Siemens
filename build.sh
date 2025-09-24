#!/bin/bash

# Build script for Order Management System
echo "🚀 Building Order Management System Executable..."

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Run the build script
python3 build_executable.py

echo "✅ Build process completed!"
