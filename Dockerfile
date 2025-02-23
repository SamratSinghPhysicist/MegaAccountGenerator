# Use a lightweight Python base image
FROM python:3.9-slim

# Install system dependencies: Chromium and Chromium-driver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Run the app with Gunicorn, binding to the PORT environment variable
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app:app"]