from flask import Flask, jsonify, request
from utils_server import get_kem_key, handle_client_message
import csv
import os

app = Flask(__name__)


@app.route("/", methods=["POST"])
def home():
    """
    Endpoint to handle client messages. Receives encrypted data, processes it, and returns the response.

    Expects:
        JSON payload with the required fields for `handle_client_message`.

    Returns:
        Flask JSON response: The processed response or an error message.
        HTTP status code: 200 on success, 500 on error.
    """
    data = request.json
    if data is None:
        return jsonify({"message": "Error"}), 500
    try:
        response, status = handle_client_message(**data)
        return jsonify(response), status
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Error"}), 500


@app.route("/keys", methods=["POST"])
def get_key():
    """
    Endpoint to retrieve the server's public key for a specified KEM algorithm.

    Expects:
        JSON payload with the field:
            - "kem_name" (str): Name of the KEM algorithm.

    Returns:
        Flask JSON response: The public key in hexadecimal format.
        HTTP status code: 200 on success, 500 on error.
    """
    data = request.json
    if data is None:
        return jsonify({"message": "Error"}), 500
    kem_name = data["kem_name"]
    return get_kem_key(kem_name)


if __name__ == "__main__":
    """
    Entry point for the Flask application. Starts the server on host 0.0.0.0 and port 5000.
    Debug mode is disabled for production use.
    """
    app.run(host="0.0.0.0", port=5000, debug=False)
