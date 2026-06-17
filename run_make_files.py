import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Directory where all the Makefiles are stored
MAKEFILES_DIR = "./Makefiles"

def run_makefile(makefile_path):
    """
    Runs a Makefile using the `make` command.

    Args:
        makefile_path (str): Path to the Makefile to execute.

    Prints:
        Success or error messages depending on the build status.
    """
    try:
        print(f"Building {makefile_path}...")
        subprocess.run(
            ["make", "-f", makefile_path],  # Run the make command with the specified Makefile
            check=True,                    # Raise an error if the command fails
            stdout=subprocess.PIPE,        # Capture standard output
            stderr=subprocess.PIPE,        # Capture standard error
        )
        print(f"Successfully built {makefile_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error building {makefile_path}:")
        print(e.stderr.decode())  # Decode and print the error message

def build_all_makefiles():
    """
    Finds and executes all Makefiles in the MAKEFILES_DIR using multithreading.

    - Ensures the required directories (`build`, `crypto_kem`, `crypto_sign`) exist.
    - Locates all Makefiles in the MAKEFILES_DIR.
    - Uses `ThreadPoolExecutor` to run Makefiles in parallel.
    """
    # Ensure the directory for Makefiles exists
    if not os.path.exists(MAKEFILES_DIR):
        print(f"Directory {MAKEFILES_DIR} does not exist.")
        return

    # Paths to ensure required build directories exist
    paths = ["./build", "./build/crypto_kem", "./build/crypto_sign"]

    # Check and create necessary directories
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)

    # Get a list of all Makefile paths
    makefile_paths = [
        os.path.join(MAKEFILES_DIR, filename)
        for filename in os.listdir(MAKEFILES_DIR)
        if filename.startswith("Makefile.")  # Only include files starting with "Makefile."
    ]

    # Run all Makefiles concurrently
    with ThreadPoolExecutor() as executor:
        executor.map(run_makefile, makefile_paths)

if __name__ == "__main__":
    """
    Entry point for the script. Executes all Makefiles found in the MAKEFILES_DIR.
    """
    build_all_makefiles()

