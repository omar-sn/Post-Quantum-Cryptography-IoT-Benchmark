use pqc_kyber::*;
use rand::rngs::OsRng;
use std::ptr;

#[no_mangle]
pub extern "C" fn encapsulate_key(
    ciphertext_ptr: *mut u8,    // Output: Pointer to buffer for ciphertext
    shared_secret_ptr: *mut u8, // Output: Pointer to buffer for shared secret
    public_key_ptr: *const u8,  // Input: Pointer to client's public key
) -> i32 {
    // Safety checks for pointers
    if public_key_ptr.is_null() || ciphertext_ptr.is_null() || shared_secret_ptr.is_null() {
        return -1; // Error: Null pointer
    }
    let mut rng = OsRng;

    unsafe {
        // Reconstruct the public key slice from the pointer
        let public_key = std::slice::from_raw_parts(public_key_ptr, KYBER_PUBLICKEYBYTES);

        // Prepare buffers for ciphertext and shared secret
        let mut ciphertext = [0u8; KYBER_CIPHERTEXTBYTES];
        let mut shared_secret = [0u8; 32];

        // Call the encapsulate function
        match encapsulate(public_key, &mut rng) {
            Ok((ct, ss)) => {
                // Copy the ciphertext and shared secret to the provided buffers
                ciphertext.copy_from_slice(&ct);
                shared_secret.copy_from_slice(&ss);

                ptr::copy_nonoverlapping(
                    ciphertext.as_ptr(),
                    ciphertext_ptr,
                    KYBER_CIPHERTEXTBYTES,
                );
                ptr::copy_nonoverlapping(shared_secret.as_ptr(), shared_secret_ptr, 32);

                0 // Success
            }
            Err(_) => -2, // Error: Encapsulation failed
        }
    }
}

#[no_mangle]
pub extern "C" fn generate_keypair(
    public_key_ptr: *mut u8, // Output: Pointer to buffer for public key
    secret_key_ptr: *mut u8, // Output: Pointer to buffer for secret key
) -> i32 {
    // Safety checks for pointers
    if public_key_ptr.is_null() || secret_key_ptr.is_null() {
        return -1; // Error: Null pointer
    }

    let mut rng = OsRng;

    unsafe {
        // Prepare buffers for public and secret keys
        let mut public_key = [0u8; KYBER_PUBLICKEYBYTES];
        let mut secret_key = [0u8; KYBER_SECRETKEYBYTES];

        // Generate the keypair
        match keypair(&mut rng) {
            Ok(keys) => {
                public_key.copy_from_slice(&keys.public);
                secret_key.copy_from_slice(&keys.secret);

                // Copy the keys to the provided buffers
                ptr::copy_nonoverlapping(public_key.as_ptr(), public_key_ptr, KYBER_PUBLICKEYBYTES);
                ptr::copy_nonoverlapping(secret_key.as_ptr(), secret_key_ptr, KYBER_SECRETKEYBYTES);

                0 // Success
            }
            Err(_) => -2, // Error: Keypair generation failed
        }
    }
}

#[no_mangle]
pub extern "C" fn decapsulate_key(
    shared_secret_ptr: *mut u8, // Output: Pointer to buffer for shared secret
    ciphertext_ptr: *const u8,  // Input: Pointer to ciphertext
    secret_key_ptr: *const u8,  // Input: Pointer to secret key
) -> i32 {
    // Safety checks for pointers
    if ciphertext_ptr.is_null() || secret_key_ptr.is_null() || shared_secret_ptr.is_null() {
        return -1; // Error: Null pointer
    }

    unsafe {
        // Reconstruct the ciphertext and secret key slices from the pointers
        let ciphertext = std::slice::from_raw_parts(ciphertext_ptr, KYBER_CIPHERTEXTBYTES);
        let secret_key = std::slice::from_raw_parts(secret_key_ptr, KYBER_SECRETKEYBYTES);

        // Prepare a buffer for the shared secret
        let mut shared_secret = [0u8; 32];

        // Call the decapsulate function
        match decapsulate(ciphertext, secret_key) {
            Ok(ss) => {
                // Copy the shared secret to the provided buffer
                shared_secret.copy_from_slice(&ss);
                ptr::copy_nonoverlapping(shared_secret.as_ptr(), shared_secret_ptr, 32);

                0 // Success
            }
            Err(_) => -2, // Error: Decapsulation failed
        }
    }
}
