import time
import ctypes
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from flask import jsonify
from libs_server import SIGNATURE_ALGORITHMS, KEM_ALGORITHMS
import csv
from dotenv import load_dotenv
import os

load_dotenv()


def hash_message(message, timings):
    """
    Computes the SHA-3 256-bit hash of the given message.

    Args:
        message (str or bytes): The message to hash.
        timings (dict): Dictionary to store timing information.

    Returns:
        bytes: The computed hash of the message.
    """
    t = time.time_ns()
    message = message.encode() if isinstance(message, str) else message
    hash_obj = hashlib.sha3_512()
    hash_obj.update(message)
    timings["server_hash_time"] = time.time_ns() - t
    return hash_obj.digest()


def verify_signature(
    sign_algorithm_name, cipher_text, signature, sign_pub_key, timings
):
    """
    Verifies the signature of a ciphertext using the specified signature algorithm.

    Args:
        sign_algorithm_name (str): Name of the signature algorithm.
        cipher_text (bytes): The ciphertext whose signature is being verified.
        signature (bytes): The signature to verify.
        sign_pub_key (bytes): The public key for signature verification.
        timings (dict): Dictionary to store timing information.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    hashed_cipher_text = hash_message(cipher_text, timings)
    verify_signature_algo = SIGNATURE_ALGORITHMS[sign_algorithm_name][
        "verify_algorithm"
    ]

    # Prepare pointers for signature, message, and public key
    sig_ptr = (ctypes.c_uint8 * len(signature)).from_buffer_copy(signature)
    sig_len = ctypes.c_size_t(len(signature))
    msg_ptr = (ctypes.c_uint8 * len(hashed_cipher_text)).from_buffer_copy(
        hashed_cipher_text
    )
    msg_len = ctypes.c_size_t(len(hashed_cipher_text))
    pk_ptr = (ctypes.c_uint8 * len(sign_pub_key)).from_buffer_copy(sign_pub_key)

    start_time = time.time_ns()
    result = verify_signature_algo(sig_ptr, sig_len, msg_ptr, msg_len, pk_ptr)
    timings["verify_time"] = time.time_ns() - start_time
    return result == 0


def decrypt_message(aes_key, iv, cipher_text, timings):
    """
    Decrypts a message using AES in CBC mode.

    Args:
        aes_key (bytes): The AES encryption key.
        iv (bytes): Initialization vector.
        cipher_text (bytes): Encrypted message.
        timings (dict): Dictionary to store timing information.

    Returns:
        str: Decrypted plaintext message.
    """
    start_time = time.time_ns()
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    message = unpad(cipher.decrypt(cipher_text), AES.block_size)
    timings["decrypt_time"] = time.time_ns() - start_time
    return message.decode("utf-8")


def decapsulate_aes_key(secret_key_encrypted, kem_algo_name, timings):
    """
    Decapsulates an encrypted AES key using the specified KEM algorithm.

    Args:
        secret_key_encrypted (bytes): The encrypted secret key.
        kem_algo_name (str): Name of the KEM algorithm.
        timings (dict): Dictionary to store timing information.

    Returns:
        bytes: The decapsulated shared secret.
    """
    kem_algo_info = KEM_ALGORITHMS[kem_algo_name]
    kem_private_key = kem_algo_info["private_key"]
    kem_algo = kem_algo_info["decapsulation_algorithm"]
    kem_algo_secret_bytes = kem_algo_info["shared_secret_bytes"]
    ss_buffer = ctypes.create_string_buffer(kem_algo_secret_bytes)

    # Prepare pointers for ciphertext and private key
    ct_ptr = (ctypes.c_uint8 * len(secret_key_encrypted)).from_buffer_copy(
        secret_key_encrypted
    )
    sk_ptr = (ctypes.c_uint8 * len(kem_private_key)).from_buffer_copy(kem_private_key)

    start_time = time.time_ns()
    result = kem_algo(ss_buffer, ct_ptr, sk_ptr)
    timings["decapsulation_time"] = time.time_ns() - start_time

    if result != 0:
        raise ValueError(f"Decapsulation failed with error code {result}")

    return ss_buffer.raw


def write_timings_to_file(
    timings,
    kem_algo_name,
    sign_algorithm_name,
    message_size,
    output_file="server_timings.csv",
):
    """
    Writes the collected timing information to a CSV file.

    Args:
        timings (dict): Timing information collected during operations.
        kem_algo_name (str): Name of the KEM algorithm used.
        sign_algorithm_name (str): Name of the signature algorithm used.
        output_file (str): Path to the output CSV file (default is 'server_timings.csv').
    """
    client_device = os.getenv("DEVICE_NAME")
    data_row = [
        kem_algo_name,
        sign_algorithm_name,
        client_device,
        timings["server_hash_time"],
        timings["verify_time"],
        timings["decapsulation_time"],
        timings["decrypt_time"],
        message_size,
    ]
    if not os.path.exists(output_file):
        with open(output_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "KEM Algorithm",
                    "Signature Algorithm",
                    "Device Name",
                    "Server Hash Time",
                    "Verify Time",
                    "Decapsulation Time",
                    "Decrypt Time",
                    "Encrypted Data Size",
                ]
            )

    with open(output_file, mode="a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_row)


def handle_client_message(
    cipher_text,
    iv,
    signature,
    secret_key,
    sign_pub_key,
    kem_algo_name,
    sign_algorithm_name,
):
    """
    Handles a client message by verifying the signature, decapsulating the key, and decrypting the message.

    Args:
        cipher_text (str): Hex-encoded ciphertext.
        iv (str): Hex-encoded initialization vector.
        signature (str): Hex-encoded signature.
        secret_key (str): Hex-encoded encrypted secret key.
        sign_pub_key (str): Hex-encoded signing public key.
        kem_algo_name (str): Name of the KEM algorithm used.
        sign_algorithm_name (str): Name of the signature algorithm used.

    Returns:
        tuple: JSON response and HTTP status code.
    """
    timings = {}
    signature_bytes = bytes.fromhex(signature)
    sign_pub_key_bytes = bytes.fromhex(sign_pub_key)
    cipher_text_bytes = bytes.fromhex(cipher_text)
    secret_key_bytes = bytes.fromhex(secret_key)
    iv_bytes = bytes.fromhex(iv)

    # Verify the signature
    if not verify_signature(
        sign_algorithm_name,
        cipher_text_bytes,
        signature_bytes,
        sign_pub_key_bytes,
        timings,
    ):
        return {"message": "Could not verify signature."}, 500

    # Decapsulate the AES key
    aes_key = decapsulate_aes_key(secret_key_bytes, kem_algo_name, timings)

    # Decrypt the message
    message = decrypt_message(aes_key[:32], iv_bytes, cipher_text_bytes, timings)

    # Write timings to a CSV file
    write_timings_to_file(timings, kem_algo_name, sign_algorithm_name, len(message))

    return {"message": message}, 200


def get_kem_key(kem_name):
    """
    Retrieves the server's public key for the specified KEM algorithm.

    Args:
        kem_name (str): Name of the KEM algorithm.

    Returns:
        Response: Flask JSON response containing the server's public key in hex format.
    """
    key = KEM_ALGORITHMS[kem_name]["public_key"]
    return jsonify({"server_public_key": key.hex()})
