= Introduction
This project explores the efficiency of Post-Quantum Cryptography (PQC) algorithms on microcontrollers. To achieve this, a benchmark was developed to test selected algorithms using real data. Additionally, a completely different implementation written in Rust, instead of C, was included for comparison.

Initially, the goal was to run these algorithms on extremely lightweight systems, such as the ESP32 or even the ESP8266. More details on this initial attempt can be found in (Doc).

This document focuses on the final results and accomplishments of the project.

After realizing that running PQC algorithms on such lightweight systems was more challenging than expected, the focus shifted to implementation on the Raspberry Pi. Throughout the project, the benchmark evolved significantly while maintaining its primary goal: simulating a real-world scenario in which an embedded system securely transmits data to a server using post-quantum-safe cryptography. The Realization section provides an overview of the mid-level implementation details.

At its core, the project aimed to establish secure communication between a client and a server, as illustrated in Figure @communication:

#figure(image("../figures/Benchmark.png"), caption:[Communication between Server and Client])<communication>

For the cryptographic algorithm implementations, the PQClean library was used. Additionally, for the Rust implementation, the Kyber library from Argyle-Software was utilized.

PQClean is a library that provides clean, portable, and secure implementations of post-quantum cryptographic algorithms. It focuses on quantum-resistant encryption, key exchange, and digital signatures, following strict coding guidelines to ensure security and auditability. The library includes implementations of NIST PQC standardization candidates while ensuring resistance to side-channel attacks. Written in standard C, PQClean is designed for portability and easy integration into security-critical applications, serving as a reliable foundation for developing and benchmarking post-quantum cryptography.


