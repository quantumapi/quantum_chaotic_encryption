# Use the official Python 3.8 slim image as the base
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy dependency specifications and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . .

# Expose a port if necessary (optional)
EXPOSE 80

# Set an environment variable for IBM Quantum API token (override at runtime)
ENV IBMQ_TOKEN=""

# Run the main script
CMD ["python", "quantum_chaotic_encryption.py"]
