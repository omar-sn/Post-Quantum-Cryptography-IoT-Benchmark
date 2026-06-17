# PQC-Bench: Post-Quantum Cryptography Benchmark on Raspberry Pi

PQC-Bench is a university research prototype for evaluating post-quantum cryptographic algorithms on Raspberry Pi devices in a realistic smart-city IoT communication scenario.

The benchmark simulates a sensor client that fetches real-world observation data, encrypts it with a shared AES key established through a post-quantum key encapsulation mechanism (KEM), signs the encrypted payload with a post-quantum signature algorithm, and sends it to a Flask server for verification, decapsulation, and decryption.

The implementation and results are connected to the peer-reviewed conference paper:

- Whitepaper / OPUS entry: [A Prototype for evaluating Post-Quantum Cryptography on resource-constrained Hardware with real-world Smart City Sensor Data](https://opus.bsz-bw.de/hft/frontdoor/index/index/year/2025/docId/1259)
- DOI: [10.5194/isprs-archives-XLVIII-4-W16-2025-113-2025](https://doi.org/10.5194/isprs-archives-XLVIII-4-W16-2025-113-2025)

## What This Project Demonstrates

- End-to-end post-quantum-protected benchmark communication workflow on embedded Linux devices.
- Python integration of C-based PQClean algorithms through `ctypes`.
- Rust-based Kyber shared libraries used alongside PQClean implementations.
- Benchmark orchestration across multiple Raspberry Pi devices using SSH and tmux.
- Measurement of key generation, encapsulation, decapsulation, encryption, hashing, signing, verification, and decryption.
- CSV-based result collection and plotting scripts for performance analysis.
- Practical comparison of PQC algorithms under constrained hardware conditions.

## Published Result Summary

The published evaluation used Raspberry Pi 3 and Raspberry Pi Zero 2 W devices with real-world smart-city sensor data. The paper reports the following practical conclusions:

| Area | Best practical result | Interpretation |
| --- | --- | --- |
| KEM key generation | Kyber family | Consistently below one second and lowest overhead among evaluated KEMs. |
| KEM encapsulation | Kyber family | Fastest and most suitable for lightweight client-side key establishment. |
| KEM decapsulation | Kyber, especially Kyber512 Rust in the paper's server-side results | Best fit for server-side decapsulation on Raspberry Pi devices. |
| Client-side signing | Dilithium family | Fastest signing behavior, important because signing happens frequently on the constrained sensor node. |
| Signature verification | Falcon, especially Falcon512 | Strongest verification performance, useful because verification normally runs on the server side. |
| Signature key generation | Falcon family | Shortest key-generation times across evaluated signature security levels. |
| Less suitable for time-sensitive IoT | McEliece, HQC, Rainbow | High computational overhead; McEliece key generation exceeds 17 seconds at higher security levels. |
| Device comparison | Raspberry Pi Zero 2 W about 20% slower than Raspberry Pi 3 | Confirms the hardware impact on PQC deployment. |

Bottom line: for constrained smart-city or IoT-style deployments, the paper identifies Kyber as the strongest KEM choice, Dilithium as highly practical for frequent signing, and Falcon as very strong for verification and key generation. McEliece, HQC, and Rainbow are useful comparison points, but they are not the practical default for low-latency embedded deployments.

## Project Context

The project was built to answer a concrete question: can modern post-quantum cryptography be used on low-resource devices without making a realistic sensor-data workflow unusable?

The benchmark uses a client-server architecture:

1. The client fetches observation data from the OGC API endpoint configured in `client.py`.
2. The client requests the server public KEM key for the selected KEM algorithm.
3. The client encapsulates a shared secret.
4. The first 32 bytes of the shared secret are used as AES key material.
5. The client encrypts the sensor payload using AES-CBC.
6. The encrypted payload is hashed with SHA3-512.
7. The hash is signed with the selected post-quantum signature algorithm.
8. The client sends ciphertext, IV, signature, signing public key, encapsulated key, and algorithm metadata to the server.
9. The server verifies the signature.
10. The server decapsulates the shared secret.
11. The server decrypts the payload.
12. Client-side and server-side timings are written to CSV files.

The current client fetches its payload once during startup from:

```text
https://ogcapi.hft-stuttgart.de/sta/udigit4icity/v1.1/Observations
```

Direct client runs therefore require network access to that endpoint, unless the URL in `client.py` is replaced.

## Architecture

![Benchmark Architecture](Dokumentation/figures/Benchmark.svg)

## Hardware Setup

The project was designed and tested on Raspberry Pi devices running Raspberry Pi OS/Linux.

| Device | Role |
| --- | --- |
| Raspberry Pi Zero 2 W | Client or server |
| Raspberry Pi 3B | Client or server |
| Additional Raspberry Pi 3B | Additional benchmark device in later tests |

The controller can run benchmark rounds in both directions by swapping client and server roles between devices.

## Technologies

- Python
- Flask
- Requests
- Paramiko
- Pandas
- Matplotlib
- PyCryptodome
- C
- Rust
- PQClean
- `ctypes`
- Raspberry Pi OS / Linux
- SSH
- tmux

## Tested Algorithms

### Key Encapsulation Mechanisms

- Kyber512, Kyber768, Kyber1024 from PQClean
- Kyber512, Kyber768, Kyber1024 Rust variants
- Classic McEliece variants:
  - `mceliece348864`
  - `mceliece460896`
  - `mceliece6688128`
  - `mceliece6960119`
  - `mceliece8192128`
- HQC-RMRS variants:
  - `hqc-rmrs-128`
  - `hqc-rmrs-192`
  - `hqc-rmrs-256`

### Digital Signature Algorithms

- Dilithium2, Dilithium3, Dilithium5
- Falcon512, Falcon1024
- Rainbow classic variants:
  - `rainbowIclassic`
  - `rainbowIIIclassic`
  - `rainbowVclassic`

Note: Rainbow is included as part of the historical benchmark comparison. It is not a modern recommendation for new post-quantum deployments.

## Repository Structure

```text
.
|-- client.py                 # Client benchmark loop, sensor-data fetch, client CSV output
|-- server.py                 # Flask server for encrypted and signed PQC communication
|-- controller.py             # SSH/tmux Raspberry Pi benchmark orchestration
|-- libs_client.py            # Client-side algorithm bindings, metadata, signature keys
|-- libs_server.py            # Server-side algorithm bindings, metadata, KEM keys
|-- utils_client.py           # Client cryptographic workflow helpers
|-- utils_server.py           # Server cryptographic workflow helpers
|-- generate_make_files.py    # Generates Makefiles for PQClean clean implementations
|-- run_make_files.py         # Builds generated PQClean Makefiles into shared libraries
|-- install_full.sh           # Current Raspberry Pi installation/build helper
|-- requirements              # Python dependency list, intentionally without .txt suffix
|-- plotting/                 # Result visualization scripts
|-- rust/                     # Rust Kyber wrapper and build scripts
|-- Dokumentation/            # Academic documentation, PDF, Typst sources, figures
`-- PQClean/                  # Vendored third-party PQClean source code
```

Generated build artifacts and benchmark outputs such as `build/`, `Makefiles/`, `rust/target/`, `.venv/`, `*.csv`, and plot folders are intentionally excluded from version control.

## Installation

### Prerequisites

The target platform is Raspberry Pi OS or another Linux environment. The Python runtime expects Linux shared libraries (`.so`) under `build/`.

Required system tools:

- Python 3
- Python virtual environment support
- GCC / build-essential
- make
- Rust toolchain
- SSH access between Raspberry Pi devices
- tmux for controller-managed benchmark runs

Typical Raspberry Pi OS setup:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip build-essential make tmux
```

Install Rust before building the Rust Kyber wrappers. On Raspberry Pi devices, the minimal Rust toolchain is enough.

### Python Setup

```bash
git clone <repository-url>
cd <repository-folder>

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements
```

### Build PQClean Libraries

```bash
python generate_make_files.py
python run_make_files.py
```

This creates generated Makefiles in:

```text
Makefiles/
```

and builds shared libraries under:

```text
build/crypto_kem/
build/crypto_sign/
```

The runtime loads the configured algorithms from `libs_client.py` and `libs_server.py`.

### Build Rust Kyber Libraries

```bash
cd rust
./build.sh
```

The Rust build creates Kyber shared libraries and copies them into:

```text
build/crypto_kem/
```

The repository also contains a Windows batch file for development experiments, but the benchmark runtime is configured for Linux/Raspberry Pi shared libraries.

### One-Step Device Setup

For Raspberry Pi benchmark devices, the current installation helper is:

```bash
./install_full.sh
```

This creates the virtual environment, installs Python dependencies, builds PQClean libraries, and builds the Rust Kyber wrappers.

## Configuration

Create a `.env` file in the project root to define the device name written into benchmark CSV files:

```env
DEVICE_NAME=Raspberry Pi 3B
```

If `DEVICE_NAME` is omitted, key-generation rows fall back to `Unknown Device`, while some client/server timing rows may contain an empty device field.

For controller-based execution, adapt `controller.py` before use:

- Raspberry Pi hostnames
- usernames
- SSH key paths or authentication method
- remote project path
- Raspberry Pi IP addresses
- benchmark duration and iteration count

The committed controller values represent the original lab environment and are not portable defaults.

## Running Directly

### Start the Server

```bash
python server.py
```

The server listens on:

```text
0.0.0.0:5000
```

### Start the Client

```bash
python client.py <SERVER_IP> [PORT]
```

Example:

```bash
python client.py 192.168.178.50 5000
```

The client fetches the observation payload once at startup and then continuously executes the benchmark workflow for all configured KEM and signature algorithm combinations.

## Running the Full Raspberry Pi Benchmark

The controller automates setup, startup, role switching, and result collection across Raspberry Pi devices:

```bash
python controller.py
```

The controller:

- connects to the Raspberry Pi devices via SSH
- runs the full installation script on each device
- starts server and client processes in tmux sessions
- swaps client and server roles between benchmark runs
- downloads generated CSV files
- combines result files into consolidated benchmark outputs

Important: `controller.py` contains lab-specific values from the original test environment. Treat it as an orchestration template, not as a drop-in production script.

## Benchmark Output

| File | Description |
| --- | --- |
| `client_timings.csv` | Client-side encapsulation, encryption, hashing, and signing timings |
| `server_timings.csv` | Server-side hashing, verification, decapsulation, and decryption timings |
| `key_generation_times.csv` | Key generation timings per algorithm and device |
| `key_sizes_client.csv` | Header file created during client setup for key-size logging |
| `key_sizes.csv` | Signature key-size rows written during client-side signature key generation |

When `client.py` and `server.py` are run directly, CSV files are written in the project root.

When `controller.py` combines files from multiple Raspberry Pis, consolidated `client_timings.csv`, `server_timings.csv`, and `key_generation_times.csv` are written to:

```text
output/
```

Timing units:

- client and server operation timings are recorded in nanoseconds
- key generation timings are recorded in seconds

## Plotting Results

After benchmark execution, the plotting scripts can generate visualizations from CSV files in the project root:

```bash
python plotting/plot_client.py
python plotting/plot_server.py
```

Generated plots are written to:

```text
clientPlots/
serverPlots/
```

`plotting/plot_key_generation.py` is an analysis helper for enriched key-generation CSV files. The raw `key_generation_times.csv` produced by the benchmark contains only `Name`, `Key Generation Time`, and `Device Name`, while that plotting script expects additional metadata columns such as algorithm type, family, and original algorithm name.

Also check units before presenting plots: the raw client/server CSV values are in nanoseconds, while some plot labels use microseconds.

## Documentation and Publication

This repository includes academic documentation artifacts:

- [Project Documentation PDF](Dokumentation/Dokumentation.pdf)
- Typst source files under `Dokumentation/`
- architecture figures under `Dokumentation/figures/`

The public research paper connected to this prototype is available here:

- [OPUS publication page](https://opus.bsz-bw.de/hft/frontdoor/index/index/year/2025/docId/1259)
- [ISPRS Archives / DOI](https://doi.org/10.5194/isprs-archives-XLVIII-4-W16-2025-113-2025)

## Third-Party Code

This repository vendors PQClean as third-party source code for post-quantum cryptographic algorithm implementations.

PQClean provides portable C implementations of post-quantum cryptographic algorithms. In this project, generated Makefiles compile selected PQClean `clean` implementations into shared libraries, which are then called from Python through `ctypes`.

The project-specific work in this repository is the benchmark workflow, Python integration, Raspberry Pi orchestration, Rust wrapper integration, result collection, plotting support, and academic documentation around the evaluation.

## Security and Reproducibility Notes

- This is an academic benchmark prototype, not production cryptographic infrastructure.
- The protocol is designed for measurement and comparison, not as a replacement for TLS, SSH, MQTT security, or a hardened production protocol.
- AES-CBC is used after KEM-based shared-secret establishment because the benchmark focuses on PQC overhead, not on designing a complete production transport layer.
- Side-channel resistance, energy usage, memory footprint, and full protocol-stack integration were outside the implemented benchmark scope.
- `controller.py` contains original lab-environment configuration and must be adapted before reuse.
- `install_full.sh` is the current setup helper. Any older controller-install helper should be treated as legacy.
- Benchmark CSV files are excluded from Git by `.gitignore`; use the linked paper for published results or rerun the benchmark to generate fresh local CSV files.

## Contributors

This repository is based on a university group project.

- Omar Haj Abdulaziz
- Jonas Möwes 
- Ayham Alhasan

Original repository: https://github.com/SirJonasM/PQC-Bench.git

The connected publication also credits Prof. Dr. Jan Seedorf, Darshana Rawal, and Thunyathep Santhanavanich as co-authors.
