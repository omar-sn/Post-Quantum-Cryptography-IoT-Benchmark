import os

# Paths to the directories containing the libraries
BASE_DIR = "./PQClean"
KEM_DIR = os.path.join(BASE_DIR, "crypto_kem")
SIGN_DIR = os.path.join(BASE_DIR, "crypto_sign")

# Template for the Makefile
MAKEFILE_TEMPLATE = """CC = gcc
CFLAGS = -Wall -Wextra -O3 -fPIC -I./PQClean/common
TARGET = ./build/{type}/lib{target}
COMMON_SRCS = ./PQClean/common/*.c

IMPL_SRCS = ./PQClean/{type}/{library}/clean/*.c

all: $(TARGET)

$(TARGET): $(IMPL_SRCS) $(COMMON_SRCS)
\t$(CC) -shared $(CFLAGS) -o $@ $(IMPL_SRCS) $(COMMON_SRCS)

clean:
\trm -f $(TARGET)
"""

# Output directory for the Makefiles
OUTPUT_DIR = "./Makefiles"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_libraries(base_dir):
    """
    Traverse the base directory to find all library paths under `clean`.

    Args:
        base_dir (str): The base directory to traverse.

    Returns:
        list: A list of tuples in the form (type, library_name), where:
            - type (str): The library type (e.g., "crypto_kem" or "crypto_sign").
            - library_name (str): The name of the library.
    """
    libraries = []
    for root, dirs, _ in os.walk(base_dir):
        for dir_name in dirs:
            if dir_name == "clean":
                # Extract type (e.g., crypto_kem or crypto_sign) and library name
                rel_path = os.path.relpath(root, BASE_DIR)
                type_name = rel_path.split(os.sep)[0]
                library_name = os.path.basename(root)
                libraries.append((type_name, library_name))
    return libraries

def create_makefile(type_name, library_name):
    """
    Generate a Makefile for the given library using the template.

    Args:
        type_name (str): The type of library (e.g., "crypto_kem" or "crypto_sign").
        library_name (str): The name of the library.

    Side Effects:
        Creates a Makefile for the specified library in the output directory.
    """
    # Define the target shared library name
    target_name = f"{library_name}.so"

    # Populate the Makefile template with the library details
    makefile_content = MAKEFILE_TEMPLATE.format(
        target=target_name,
        type=type_name,
        library=library_name
    )
    
    # Save the generated Makefile to the output directory
    makefile_path = os.path.join(OUTPUT_DIR, f"Makefile.{library_name}")
    with open(makefile_path, "w") as makefile:
        makefile.write(makefile_content)

    print(f"Makefile created for {type_name}/{library_name}: {makefile_path}")

def main():
    """
    Main script logic to find libraries and generate Makefiles.

    - Collects libraries from `crypto_kem` and `crypto_sign` directories.
    - Creates a Makefile for each library in the output directory.
    """
    # Collect libraries from the KEM and SIGN directories
    kem_libraries = find_libraries(KEM_DIR)
    sign_libraries = find_libraries(SIGN_DIR)

    # Combine all libraries into a single list
    all_libraries = kem_libraries + sign_libraries

    # Generate Makefiles for each library
    for type_name, library_name in all_libraries:
        create_makefile(type_name, library_name)

if __name__ == "__main__":
    """
    Entry point for the script. Ensures that Makefiles are generated for all libraries
    under the `crypto_kem` and `crypto_sign` directories in the PQClean base structure.
    """
    main()

