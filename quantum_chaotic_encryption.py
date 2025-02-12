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
import time
import logging
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Set up logging
logging.basicConfig(filename="quantum_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

print("🚀 Quantum-Chaotic Cryptographic Engine Starting...\n")

# Initialize Qiskit Service
try:
    service = QiskitRuntimeService()
    logging.info("✅ Qiskit Runtime Service initialized successfully.")
    print("✅ Qiskit Runtime Service initialized.")
except Exception as e:
    logging.error(f"❌ Failed to initialize Qiskit Runtime Service: {e}")
    print(f"❌ Qiskit Runtime Service failed to initialize: {e}")
    service = None

# Select a backend
def get_backend():
    try:
        backends = service.backends(simulator=False)
        backend = min(backends, key=lambda b: b.status().pending_jobs)
        logging.info(f"✅ Selected backend: {backend.name}")
        print(f"✅ Using backend: {backend.name}")
        return backend
    except Exception as e:
        logging.error(f"❌ Error selecting backend: {e}")
        print(f"❌ Error selecting backend: {e}")
        return None

# Generate quantum random bits
def generate_quantum_random_bits(bits_per_run=8, runs=32, max_retries=5):
    """
    Generates a bitstring of length (bits_per_run * runs) using quantum measurements.
    """
    backend = get_backend()
    
    if backend is None:
        logging.error("⚠️ No available quantum backend. Falling back to classical randomness.")
        print("⚠️ No quantum backend available. Using classical randomness.")
        return np.random.randint(0, 2, bits_per_run * runs).tolist()

    print("🚀 Running quantum randomness generation...")
    bitstring = ""

    retries = 0
    while retries < max_retries:
        try:
            sampler = Sampler()
            for i in range(runs):
                qc = QuantumCircuit(bits_per_run)
                qc.h(range(bits_per_run))  # Apply Hadamard gate
                qc.measure_all()

                transpiled_qc = transpile(qc, backend)
                job = sampler.run([transpiled_qc], shots=1)
                result = job.result()

                # Extract quantum bits
                measured_bits = "".join(str(b) for b in result.quasi_dists[0].keys())
                bitstring += measured_bits[::-1]  # Reverse endianness

                print(f"✅ Circuit {i+1}/{runs} completed: {measured_bits}")

            logging.info(f"✅ Quantum randomness generated: {bitstring}")
            return bitstring
        except Exception as e:
            logging.error(f"❌ Quantum sampling failed: {e}")
            print(f"❌ Error extracting quantum bits: {e} - Retrying ({retries+1}/{max_retries})...")
            retries += 1
            time.sleep(2)

    print("⚠️ Max retries reached. Falling back to classical randomness.")
    logging.error("⚠️ Max retries reached. Falling back to classical randomness.")
    return np.random.randint(0, 2, bits_per_run * runs).tolist()

# Chaotic scrambling function
def chaotic_scramble(bit_str, iterations=100, r=4.0):
    """
    Processes the raw quantum bitstring through a logistic map for chaotic diffusion.
    """
    print("🔄 Applying chaotic entropy diffusion...")
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
    print(f"✅ Scrambled bits: {scrambled_bits[:64]}... (truncated)")
    return scrambled_bits

# AES Key Derivation
def derive_aes_key(bit_str):
    """
    Converts a 256-bit bitstring into a 32-byte key for AES-256.
    """
    print("🔑 Deriving AES-256 key...")
    if len(bit_str) != 256:
        raise ValueError("Bitstring must be exactly 256 bits for AES-256 key derivation.")
    key_int = int(bit_str, 2)
    key = key_int.to_bytes(32, byteorder='big')
    print(f"✅ AES Key (hex): {key.hex()}")
    return key

# AES Encryption
def encrypt_message(plaintext, key):
    """
    Encrypts a plaintext message using AES-GCM.
    """
    print("🔐 Encrypting message with AES-GCM...")
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    print(f"✅ Ciphertext: {ciphertext.hex()}")
    return {'nonce': cipher.nonce, 'ciphertext': ciphertext, 'tag': tag}

# AES Decryption
def decrypt_message(enc_data, key):
    """
    Decrypts data encrypted with AES-GCM.
    """
    print("🔓 Decrypting message...")
    cipher = AES.new(key, AES.MODE_GCM, nonce=enc_data['nonce'])
    plaintext = cipher.decrypt_and_verify(enc_data['ciphertext'], enc_data['tag'])
    print(f"✅ Decrypted message: {plaintext.decode('utf-8')}")
    return plaintext.decode('utf-8')

# Main function
def main():
    print("\n🚀 Step 1: Generating raw quantum randomness...\n")
    raw_bits = generate_quantum_random_bits(bits_per_run=8, runs=32)

    print("\n🔄 Step 2: Diffusing entropy via chaotic mapping...")
    scrambled_bits = chaotic_scramble(raw_bits, iterations=100, r=4.0)

    print("\n🔑 Step 3: Deriving AES-256 Key...")
    aes_key = derive_aes_key(scrambled_bits)

    sample_message = "Revolutionary quantum-cryptographic protocols are operational."
    print("\n🔐 Step 4: Encrypting message...")
    enc_data = encrypt_message(sample_message, aes_key)

    print("\n🔓 Step 5: Decrypting message...")
    decrypted_message = decrypt_message(enc_data, aes_key)

    print("\n✅ All operations completed successfully!")

if __name__ == '__main__':
    main()
