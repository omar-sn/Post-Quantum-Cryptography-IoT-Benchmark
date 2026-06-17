= Further Notes
This section provides important details to ensure the benchmark runs correctly.

== Environment Files (.env)
- Create .env files in the respective directories with the following format:
```env
DEVICE_NAME=<Device name>
```
- The server and client retrieve their names from these files to correctly log data in the CSV files.
== Controller Script and Installation Process
- The controller script includes a shell script that ensures all required dependencies are installed before running the benchmark.
- If any installation step fails, the benchmark will not start to prevent incomplete or inconsistent results.
- The controller script automatically performs the full installation process, including:
  - Compiling the necessary binaries from the PQClean library.
  - Building the Rust wrapper.
== SSH Authentication
- The controller script authenticates via SSH keys.
- RSA keys seem to cause issues with authentication.
- Instead, generate an Ed25519 SSH key using the following command:
```sh
ssh-keygen -t ed25519
```
== Rust installation
- Install only the minimal Rust toolchain on the Raspberry Pis, as the full toolchain is too large and unnecessary for this project.
