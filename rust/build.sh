#!/usr/bin/bash

# Output directory
OUTPUT_DIR="../build/crypto_kem"

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Run cargo builds for each manifest
echo "Building with Cargo.512.toml..."
echo "Building with Cargo.toml..."
cp Cargo-512.toml Cargo.toml
cargo build --release 

echo "Building with Cargo-768.toml..."
cp Cargo-768.toml Cargo.toml
cargo build --release 

echo "Building with Cargo.1024.toml..."
cp Cargo-1024.toml Cargo.toml
cargo build --release 

cp Cargo-768.toml Cargo.toml

# Copy all .so files to the output directory
echo "Copying .so files to $OUTPUT_DIR..."
cp target/release/*.so "$OUTPUT_DIR"

echo "All builds and copy completed successfully!"
