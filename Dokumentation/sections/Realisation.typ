= Realisation
== General Setup
As Hardware we had at the start a Raspberry Pi Zero 2 W and a Raspberry Pi 3B.
Later we got a second Raspberry Pi 3B.

Due to much capabilities of the Raspberry Pis we were able to run a simple Python Flask server and make requests to it with the requests library of Python.

== Required Packages
The following Python packages were required for the implementation:
- pycryptodome 
- flask
- requests
- paramiko
- pandas
- python-dotenv 

== Compiling C-Based PQClean Algorithms
To execute the PQClean library’s C-based algorithms from Python, the ctypes module was used. The C source files needed to be compiled beforehand. To automate this process, Python scripts were written to generate a Makefile for each algorithm and execute make.

This process resulted in a build directory containing two subdirectories:

crypto_sign/ (for signature mechanisms)
crypto_kem/ (for key encapsulation mechanisms)
Since PQClean follows a strict guideline for function interfaces, calling the compiled implementations was straightforward.

=== Function Headers for Key Encapsulation Mechanism (KEM)
The function headers for KEM algorithms in PQClean always follow this format:
```C
  int PQCLEAN_NAME_CLEAN_crypto_kem_keypair(uint8_t *pk, uint8_t *sk);
  int PQCLEAN_NAME_CLEAN_crypto_kem_enc(uint8_t *ct, uint8_t *ss, const
uint8_t *pk);
  int PQCLEAN_NAME_CLEAN_crypto_kem_dec(uint8_t *ss, const uint8_t *ct,
const uint8_t *sk);
```
For example, the function headers for Kyber512 are:
```C
int PQCLEAN_KYBER512_CLEAN_crypto_kem_keypair(uint8_t *pk, uint8_t *sk);
int PQCLEAN_KYBER512_CLEAN_crypto_kem_enc(uint8_t *ct, uint8_t *ss, const
uint8_t *pk);
int PQCLEAN_KYBER512_CLEAN_crypto_kem_dec(uint8_t *ss, const uint8_t *ct,
const uint8_t *sk);
```
=== Function Headers for Digital Signature Mechanism
For post-quantum signatures, PQClean provides the following standard function headers:
```C
int PQCLEAN_NAME_CLEAN_crypto_sign_signature(
    uint8_t *sig, size_t *siglen,
    const uint8_t *m, size_t mlen, const uint8_t *sk);

int PQCLEAN_NAME_CLEAN_crypto_sign_verify(
    const uint8_t *sig, size_t siglen,
    const uint8_t *m, size_t mlen, const uint8_t *pk);

int PQCLEAN_NAME_CLEAN_crypto_sign(
    uint8_t *sm, size_t *smlen,
    const uint8_t *m, size_t mlen, const uint8_t *sk);
```
For Dilithium2, the corresponding function headers are:
```C
int PQCLEAN_DILITHIUM2_CLEAN_crypto_sign_signature(
    uint8_t *sig, size_t *siglen,
    const uint8_t *m, size_t mlen, const uint8_t *sk);

int PQCLEAN_DILITHIUM2_CLEAN_crypto_sign_verify(
    const uint8_t *sig, size_t siglen,
    const uint8_t *m, size_t mlen, const uint8_t *pk);

int PQCLEAN_DILITHIUM2_CLEAN_crypto_sign(
    uint8_t *sm, size_t *smlen,
    const uint8_t *m, size_t mlen, const uint8_t *sk);
```
== Rust Implementation
The Rust-based implementation follows a different interface. To accommodate this, a wrapper was created in the Rust directory. A shell script was also developed to compile this wrapper and generate the necessary binaries. These binaries are then moved into the _build/crypto_kem/_ directory.

(See Further Notes for Rust installation details.)
== First implementation
The first implementation differed significantly from the final result. The communication between the server and client in this initial version is shown in Figure @first:

#figure(image("../figures/Draw-1.png"), caption: [First Implementation])<first>

=== Initial Communication Flow
1. The server receives a public key for a key encapsulation mechanism (KEM) and returns encrypted data.
2. The server also signs the hash of the encrypted content.
3. The server benchmarks several operations, including:
    - Performing key encapsulation
    - Encrypting data
    - Hashing the encrypted data
    - Signing the hash
4. The benchmark results are sent back to the client.
5. The client verifies and decrypts the response while also measuring execution time.
6. All timing results are saved to a file.
=== Problem with the Initial Implementation
While this implementation successfully performed post-quantum encryption and benchmarking, the client-server roles were misaligned.

- In this setup, the server was responsible for measuring data (e.g., temperature) and waiting for the client to request it.
- This meant that each device would need to run a server, which is not ideal for real-world applications.
A more practical solution would be for the sensor device (measuring temperature) to act as the client, while the data-collecting device acts as the server.
== Final Implementation
The final implementation follows the improved client-server model, as illustrated in Figure @communication:

As mentioned the client and the server only once (at the start) generate their keys. So it would be nice to restart server and client to also compare the key generation times of the algorithms. Also especially when using two different devices it would me nice if the server and client role of the device would swap. 
As mentioned the client and the server only once (at the start) generate their keys. So it would be nice to restart server and client to also compare the key generation times of the algorithms. Also especially when using two different devices it would me nice if the server and client role of the device would swap. 

You could now do this by hand by restarting the server and client in an intervall. But creating the keys on these  lightweight devices takes a lot of time (See Evaluation) so this is not recommended. Instead there is a Controller script that uses ssh and scp to manage the benchmark and orchestrate the files created by the server and client. This controller script depends on the way your devices are set up. To use it you need to specify the host name and the location of your ssh keys establish an connection with the devices. In the controller script you can set the nbumber of iterations and the time for each iteration.

At the start of the script the controller deletes all csv file in the directory on the devices so be carefull.

When finished with the benchmark it downloads all created files and puts them together. 

This creates the following CSV-Files: 

You could now do this by hand by restarting the server and client in an intervall. But creating the keys on these  lightweight devices takes a lot of time (See Evaluation) so this is not recommended. Instead there is a Controller script that uses ssh and scp to manage the benchmark and orchestrate the files created by the server and client. This controller script depends on the way your devices are set up. To use it you need to specify the host name and the location of your ssh keys establish an connection with the devices. In the controller script you can set the nbumber of iterations and the time for each iteration.

At the start of the script the controller deletes all csv file in the directory on the devices so be carefull.

When finished with the benchmark it downloads all created files and puts them together. 

This creates the following CSV-Files: 

=== Communication Flow
1. The client requests a public key for a key encapsulation mechanism (KEM).
2. Using this public key, the client generates an AES key and encapsulates it.
3. The AES key is then used to encrypt the data.
4. The encrypted data is hashed and signed using a post-quantum signature mechanism.
5. Each process is timed, and the results are saved to a CSV file.
6. The client sends the following data to the server:
    - Encrypted data
    - Signature
    - Public signature key
    - Used signature and KEM algorithms
    - Encapsulated AES key
    - IV (Initialization Vector)
7. The server:
    - Hashes the encrypted data and verifies the signature.
    - Decapsulates the AES key and decrypts the data.
    - Measures execution time and logs it in a CSV file.

At startup, both the server and client generate and log the key pair generation times for each algorithm.

To run the benchmark, install the server on Device A and the client on Device B. Then:

- Start the server on Device A
- Start the client on Device B
The benchmark runs continuously until the client is stopped.

== Controller
Since the server and client only generate their keys once at startup, comparing key generation times between algorithms requires restarting both processes.

=== Automating Benchmark Execution
- Manually restarting the server and client at intervals is not practical, especially on lightweight devices where key generation is time-consuming (see Evaluation).
- Instead, a Controller Script automates this process.
=== Controller Script Features
- Uses SSH and SCP to manage the benchmark and collect generated files.
- Configurable settings:
    - Hostnames
    - SSH key locations
    - Number of iterations
    - Time per iteration
- At the start of execution, the controller deletes all CSV files on the devices (⚠ caution advised).
Once the benchmark completes, the script downloads and consolidates all generated files into the following CSV files:

- client_timings.csv
- server_timings.csv
- key_generation_times.csv
