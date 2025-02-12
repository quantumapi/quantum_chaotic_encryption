from setuptools import setup, find_packages

setup(
    name="quantum_chaotic_encryption",
    version="0.1.0",
    description="A hybrid cryptographic engine combining IBM Quantum randomness and chaotic dynamics for AES-GCM encryption.",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/quantum-chaotic-encryption",
    packages=find_packages(),
    install_requires=[
        "qiskit>=0.44.1",
        "pycryptodome"
    ],
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
