#!/bin/bash
set -e  # Exit on any error

echo "Starting full installation..."

python3 -m venv .venv

source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements

# Generate and run make files
echo "Generating and running make files..."
python3 generate_make_files.py
python3 run_make_files.py

# Build Rust components
echo "Building Rust components..."
cd rust
./build.sh

echo "Installation completed."
