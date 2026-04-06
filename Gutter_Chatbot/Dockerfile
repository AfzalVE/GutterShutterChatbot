# Use lightweight Python image
FROM python:3.10-slim

# Prevent Python from buffering logs (important for HF logs)
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (optional but useful)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire app
COPY . .

# Hugging Face expects port 7860
EXPOSE 7860

# Set environment variable for Flask
ENV PORT=7860

# Run the Flask app
CMD ["python", "app.py"]