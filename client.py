from libs_client import KEM_ALGORITHMS, SIGNATURE_ALGORITHMS
from utils_client import send_data
import csv
import time
import sys
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# URL for data fetch
url = "https://ogcapi.hft-stuttgart.de/sta/udigit4icity/v1.1/Observations"


def fetch():
    """
    Fetches raw data from a specified URL.

    Returns:
        bytes: UTF-8 encoded data from the URL.

    Raises:
        Exception: If there is an error during the request.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        # Ensure UTF-8 decoding
        text_data = response.text
        return text_data.encode("utf-8")
    except Exception as e:
        print(f"Error fetching data: {e}")


# Fetch the raw data on initialization
RAW_DATA = fetch()


def check_and_write_csv(file_name, header):
    """
    Ensures a CSV file exists with the specified header. Creates the file if it doesn't exist.

    Args:
        file_name (str): The name of the CSV file.
        header (list of str): List of column headers for the CSV file.
    """
    if not os.path.exists(file_name):
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)


def file_setup():
    """
    Sets up necessary CSV files for logging key generation times, client timings, and key sizes.

    Files created:
        - "key_generation_times.csv" for key generation times.
        - "client_timings.csv" for client operation timings.
        - "key_sizes_client.csv" for logging key sizes.
    """
    check_and_write_csv(
        "client_timings.csv",
        [
            "KEM Algorithm",
            "Signature Algorithm",
            "Device Name",
            "Encapsulation Time",
            "Encryption Time",
            "Client Hash Time",
            "Sign Time",
            "Data Size",
        ],
    )
    with open("key_sizes_client.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", "public_key_size", "secret_key_size"])


def write_timings(timings, kem_algorithm, sign_algorithm):
    """
    Writes timing information for client operations to a CSV file.

    Args:
        timings (dict): Timing information from operations.
        kem_algorithm (str): Identifier for the KEM algorithm used.
        sign_algorithm (str): Identifier for the signature algorithm used.
    """
    client_device = os.getenv("DEVICE_NAME")
    with open("client_timings.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                kem_algorithm,
                sign_algorithm,
                client_device,
                timings["encapsulation_time"],
                timings["encryption_time"],
                timings["client_hash_time"],
                timings["sign_time"],
                len(RAW_DATA),
            ]
        )


def run(url):
    """
    Iterates over all KEM and signature algorithms, sending data to the server and logging timings.

    Args:
        url (str): Server URL.
    """
    for kem_algorithm in KEM_ALGORITHMS.values():
        for sign_algorithm in SIGNATURE_ALGORITHMS.values():
            try:
                # Send data and capture response and timings
                message, timings = send_data(
                    RAW_DATA,
                    kem_algorithm["identifier"],
                    kem_algorithm["encapsulation_algorithm"],
                    kem_algorithm["cipher_text_bytes"],
                    kem_algorithm["shared_secret_bytes"],
                    sign_algorithm["identifier"],
                    sign_algorithm["sign_algorithm"],
                    sign_algorithm["public_key"],
                    sign_algorithm["private_key"],
                    sign_algorithm["signature_bytes"],
                    url,
                )
                # Log the timings
                write_timings(
                    timings, kem_algorithm["identifier"], sign_algorithm["identifier"]
                )
            except Exception as e:
                print("Error with", kem_algorithm["identifier"], str(e))
                print("Server Error, maybe Restarting")
                time.sleep(5)


def main():
    """
    Entry point for the client application. Sets up necessary files, processes command-line arguments,
    and continuously sends data to the server.

    Command-Line Usage:
        python client.py <SERVER_IP> [PORT=5000]

    Args:
        SERVER_IP (str): The IP address of the server.
        PORT (int, optional): The port number to use (default is 5000).
    """
    if len(sys.argv) < 2:
        print("Usage: python client.py <SERVER_IP> [PORT=5000]")
        return

    server_ip = sys.argv[1]
    port = 5000
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])

    url = f"http://{server_ip}:{port}/"
    file_setup()

    # Continuously send data to the server
    while True:
        run(url)


if __name__ == "__main__":
    """
    Initializes and runs the client application if the script is executed directly.
    """
    main()
