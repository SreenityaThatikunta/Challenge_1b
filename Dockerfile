# Dockerfile for Challenge 1b PDF Analysis Pipeline
FROM python:3.11-slim

# System dependencies for PyPDF2 and subprocess
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline code and collections
COPY main.py ./
COPY Collection* ./

# Entrypoint: run the pipeline
CMD ["python", "main.py"]
