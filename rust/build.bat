@echo off

REM Output directory
set OUTPUT_DIR=..\build\crypto_kem

REM Ensure the output directory exists
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

REM Run cargo builds for each manifest
echo Building with Cargo-512.toml...
copy /Y Cargo-512.toml Cargo.toml
cargo build --release

echo Building with Cargo-768.toml...
copy /Y Cargo-768.toml Cargo.toml
cargo build --release

echo Building with Cargo-1024.toml...
copy /Y Cargo-1024.toml Cargo.toml
cargo build --release

REM Reset to Cargo-768.toml
copy /Y Cargo-768.toml Cargo.toml

REM Copy all .so files to the output directory
echo Copying .so files to %OUTPUT_DIR%...
for %%f in (target\release\*.so) do copy /Y %%f "%OUTPUT_DIR%"

echo All builds and copy completed successfully!
pause

