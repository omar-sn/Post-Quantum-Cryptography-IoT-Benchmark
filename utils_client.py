import time
import requests
import ctypes
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def hash_message(message, timings):
    """
    Computes the SHA-3 256-bit hash of the given message.

    Args:
        message (str or bytes): The message to be hashed.
        timings (dict): Dictionary to store timing information.

    Returns:
        bytes: The computed hash of the message.
    """
    t = time.time_ns()
    message = message.encode() if isinstance(message, str) else message
    hash_obj = hashlib.sha3_512()
    hash_obj.update(message)
    timings["client_hash_time"] = time.time_ns() - t
    return hash_obj.digest()


def encrypt_data(aes_key, raw_data, timings):
    """
    Encrypts raw data using AES encryption in CBC mode.

    Args:
        aes_key (bytes): The AES encryption key (32 bytes).
        raw_data (bytes): The raw data to encrypt.
        timings (dict): Dictionary to store timing information.

    Returns:
        tuple: The ciphertext and initialization vector (IV).
    """
    start_time = time.time_ns()
    cipher = AES.new(aes_key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(raw_data, AES.block_size))
    timings["encryption_time"] = time.time_ns() - start_time
    return ciphertext, cipher.iv


def encapsulate_key(
    client_public_key,
    encapsulate_algorithm,
    cipher_text_bytes,
    shared_secret_bytes,
    timings,
):
    """
    Encapsulates a key using a given algorithm and client public key.

    Args:
        client_public_key (bytes): The client's public key.
        encapsulate_algorithm (function): Function to perform the encapsulation.
        cipher_text_bytes (int): Size of the ciphertext buffer.
        shared_secret_bytes (int): Size of the shared secret buffer.
        timings (dict): Dictionary to store timing information.

    Returns:
        tuple: The encapsulated key and shared secret.
    """
    start_time = time.time_ns()
    encapsulated_key = ctypes.create_string_buffer(cipher_text_bytes)
    shared_secret = ctypes.create_string_buffer(shared_secret_bytes)
    result = encapsulate_algorithm(encapsulated_key, shared_secret, client_public_key)
    if result != 0:
        raise ValueError("Encapsulation failed")
    timings["encapsulation_time"] = time.time_ns() - start_time

    return encapsulated_key.raw, shared_secret.raw


def get_client_public_key(kem_name, url):
    """
    Fetches the client's public key from the server.

    Args:
        kem_name (str): The name of the KEM algorithm.
        url (str): The server's URL.

    Returns:
        bytes: The client's public key as bytes.
    """
    payload = {"kem_name": kem_name}
    response = requests.post(f"{url}/keys", json=payload)
    data = response.json()
    if not data or "server_public_key" not in data:
        raise ValueError("Missing 'server_public_key' in response")
    return bytes.fromhex(data["server_public_key"])


def get_data_to_send(
    raw_data,
    server_public_key,
    encapsulation_algorithm,
    cipher_text_bytes,
    shared_secret_bytes,
    sign_algorithm,
    sign_public_key,
    sign_private_key,
    sign_bytes,
):
    """
    Prepares the data to be sent to the server by encrypting, hashing, and signing it.

    Args:
        raw_data (bytes): The raw data to encrypt.
        server_public_key (bytes): The server's public key.
        encapsulation_algorithm (function): Key encapsulation function.
        cipher_text_bytes (int): Ciphertext buffer size.
        shared_secret_bytes (int): Shared secret buffer size.
        sign_algorithm (function): Signing algorithm.
        sign_public_key (bytes): Public key for signing.
        sign_private_key (bytes): Private key for signing.
        sign_bytes (int): Signature buffer size.

    Returns:
        tuple: The payload dictionary and timings.
    """
    timings = {}
    encapsulated_key, shared_secret = encapsulate_key(
        server_public_key,
        encapsulation_algorithm,
        cipher_text_bytes,
        shared_secret_bytes,
        timings,
    )
    ciphertext, iv = encrypt_data(shared_secret[:32], raw_data, timings)

    hashed_ciphertext = hash_message(ciphertext, timings)

    signature = sign_message(
        hashed_ciphertext, sign_algorithm, sign_private_key, sign_bytes, timings
    )

    return {
        "cipher_text": ciphertext.hex(),
        "iv": iv.hex(),
        "signature": signature.hex(),
        "secret_key": encapsulated_key.hex(),
        "sign_pub_key": sign_public_key.hex(),
    }, timings


def send_data(
    raw_data,
    kem_algo_name,
    kem_algorithm,
    kem_cipher_text_bytes,
    kem_shared_secret_bytes,
    sign_algorithm_name,
    sign_algorithm,
    sign_public_key,
    sign_private_key,
    sign_bytes,
    url,
):
    """
    Sends encrypted, signed, and encapsulated data to the server.

    Args:
        raw_data (bytes): The raw data to send.
        kem_algo_name (str): Name of the KEM algorithm.
        kem_algorithm (function): Key encapsulation function.
        kem_cipher_text_bytes (int): Ciphertext buffer size for KEM.
        kem_shared_secret_bytes (int): Shared secret buffer size for KEM.
        sign_algorithm_name (str): Name of the signing algorithm.
        sign_algorithm (function): Signing function.
        sign_public_key (bytes): Public key for signing.
        sign_private_key (bytes): Private key for signing.
        sign_bytes (int): Signature buffer size.
        url (str): Server URL.

    Returns:
        tuple: Server response message and timings.
    """
    client_public_key = get_client_public_key(kem_algo_name, url)
    payload, timings = get_data_to_send(
        raw_data,
        client_public_key,
        kem_algorithm,
        kem_cipher_text_bytes,
        kem_shared_secret_bytes,
        sign_algorithm,
        sign_public_key,
        sign_private_key,
        sign_bytes,
    )
    payload["kem_algo_name"] = kem_algo_name
    payload["sign_algorithm_name"] = sign_algorithm_name
    response = requests.post(f"{url}", json=payload)
    data = response.json()
    if not data or "message" not in data:
        raise ValueError("Missing 'server_public_key' in response")
    return data["message"], timings


def sign_message(message, sign_algorithm, private_key, signature_bytes, timings):
    """
    Signs a message using the provided signing algorithm and private key.

    Args:
        message (bytes): The message to sign.
        sign_algorithm (function): Signing algorithm.
        private_key (bytes): Private key for signing.
        signature_bytes (int): Signature buffer size.
        timings (dict): Dictionary to store timing information.

    Returns:
        bytes: The signature of the message.
    """
    signature = ctypes.create_string_buffer(signature_bytes)
    sig_len = ctypes.c_size_t()
    start_time = time.time_ns()
    result = sign_algorithm(
        signature, ctypes.byref(sig_len), message, len(message), private_key
    )
    if result != 0:
        raise ValueError("Signing failed")
    timings["sign_time"] = time.time_ns() - start_time
    return signature.raw[: sig_len.value]

