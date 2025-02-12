#!/usr/bin/env python3
"""
Quantum-Chaotic Cryptographic Engine 🔐⚛️

This module demonstrates a hybrid approach to secure key generation by:
  1. Harvesting 256 bits of raw quantum randomness using IBM Quantum hardware.
  2. Diffusing that entropy with a logistic map (chaotic dynamics).
  3. Deriving an AES-256 key and encrypting a sample message using AES-GCM.

Before running:
  - Ensure Python 3.8+ is installed.
  - Set your IBM Quantum API token as an environment variable: IBMQ_TOKEN.
  - Install the required dependencies:
      pip install qiskit qiskit-ibm-runtime pycryptodome
"""

import os
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def generate_quantum_random_bits(bits_per_run=8, runs=32):
    """
    Generates a bitstring of length (bits_per_run * runs) using quantum measurements.

    Args:
        bits_per_run (int): Number of qubits per circuit run.
        runs (int): Total number of independent circuit executions.

    Returns:
        str: A concatenated bitstring representing raw quantum bits.
    """
    print("Initializing Qiskit Runtime Service...")
    service = QiskitRuntimeService()

    print("Selecting least busy backend...")
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=bits_per_run)
    print(f"Using backend: {backend.name}")

    bitstring = ""

    print("Starting quantum randomness generation...")
    with Session(backend=backend) as session:
        sampler = Sampler(mode=session)

        for _ in range(runs):
            qc = QuantumCircuit(bits_per_run, bits_per_run)
            qc.h(range(bits_per_run))  # Apply Hadamard to all qubits for superposition.
            qc.measure(range(bits_per_run), range(bits_per_run))

            # Transpile circuit for backend compatibility
            qc_transpiled = transpile(qc, backend=backend)

            # Run the transpiled circuit
            job = sampler.run([qc_transpiled])
            result = job.result()

            # ✅ Debugging Output
            print(f"Quantum Result: {result}")

            # ✅ FIX: Properly extract measurement results
            bit_array = np.array(result[0].data.c).reshape(-1)  # Flatten correctly
            measured_bits = "".join(map(str, bit_array))  # Convert to string
            bitstring += measured_bits[::-1]  # Reverse due to Qiskit endianness

    print(f"Generated raw quantum bits: {bitstring}")
    return bitstring

def chaotic_scramble(bit_str, iterations=100, r=4.0):
    """
    Processes the raw quantum bitstring through a logistic map for chaotic diffusion.

    Args:
        bit_str (str): Input bitstring (expected to be 256 bits).
        iterations (int): Number of logistic map iterations.
        r (float): Logistic map parameter (r=4.0 for full chaos).

    Returns:
        str: A new 256-bit string representing the diffused entropy.
    """
    print("Applying chaotic entropy diffusion...")
    bit_length = len(bit_str)
    seed_int = int(bit_str, 2)
    max_int = 2**bit_length - 1
    x = seed_int / max_int

    for _ in range(iterations):
        x = r * x * (1 - x)
        if x in [0.0, 1.0]:  # Reinitialize if degeneracy occurs
            x = get_random_bytes(1)[0] / 255.0

    scrambled_int = int(x * (2**bit_length))
    scrambled_bits = format(scrambled_int, f'0{bit_length}b')
    print(f"Scrambled bits: {scrambled_bits}")
    return scrambled_bits

def derive_aes_key(bit_str):
    """
    Converts a 256-bit bitstring into a 32-byte key for AES-256.

    Args:
        bit_str (str): A 256-bit string.

    Returns:
        bytes: A 32-byte key.
    """
    print("Deriving AES-256 key...")
    if len(bit_str) != 256:
        raise ValueError("Bitstring must be exactly 256 bits for AES-256 key derivation.")
    key_int = int(bit_str, 2)
    key = key_int.to_bytes(32, byteorder='big')
    print(f"AES Key (hex): {key.hex()}")
    return key

def encrypt_message(plaintext, key):
    """
    Encrypts a plaintext message using AES-GCM.

    Args:
        plaintext (str): The plaintext message.
        key (bytes): A 32-byte AES key.

    Returns:
        dict: Contains nonce, ciphertext, and authentication tag.
    """
    print("Encrypting message with AES-GCM...")
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    print(f"Ciphertext: {ciphertext.hex()}")
    return {'nonce': cipher.nonce, 'ciphertext': ciphertext, 'tag': tag}

def decrypt_message(enc_data, key):
    """
    Decrypts data encrypted with AES-GCM.

    Args:
        enc_data (dict): Dictionary with keys 'nonce', 'ciphertext', and 'tag'.
        key (bytes): A 32-byte AES key.

    Returns:
        str: The decrypted plaintext.
    """
    print("Decrypting message...")
    cipher = AES.new(key, AES.MODE_GCM, nonce=enc_data['nonce'])
    plaintext = cipher.decrypt_and_verify(enc_data['ciphertext'], enc_data['tag'])
    print(f"Decrypted message: {plaintext.decode('utf-8')}")
    return plaintext.decode('utf-8')

def main():
    print("🚀 Quantum-Chaotic Cryptographic Engine Starting...\n")

    print("Step 1: Generating raw quantum randomness...")
    raw_bits = generate_quantum_random_bits(bits_per_run=8, runs=32)

    print("\nStep 2: Diffusing entropy via chaotic mapping...")
    scrambled_bits = chaotic_scramble(raw_bits, iterations=100, r=4.0)

    print("\nStep 3: Deriving AES-256 Key...")
    aes_key = derive_aes_key(scrambled_bits)

    sample_message = "Revolutionary quantum-cryptographic protocols are operational."
    print("\nStep 4: Encrypting message...")
    enc_data = encrypt_message(sample_message, aes_key)

    print("\nStep 5: Decrypting message...")
    decrypted_message = decrypt_message(enc_data, aes_key)

    print("\n✅ All operations completed successfully!")

if __name__ == '__main__':
    main()
