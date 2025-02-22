# Use an official Ubuntu base image
FROM ubuntu:20.04

# Set working directory
WORKDIR /app

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    unzip \
    curl \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1

# Install Chrome 113 explicitly
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_113.0.5672.126-1_amd64.deb && \
    apt-get install -y ./google-chrome-stable_113.0.5672.126-1_amd64.deb && \
    rm google-chrome-stable_113.0.5672.126-1_amd64.deb

# Install ChromeDriver 113.0.5672.24
RUN CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+') && \
    echo "Chrome version: $CHROME_VERSION" && \
    CHROMEDRIVER_VERSION="113.0.5672.24" && \
    echo "Hardcoded ChromeDriver version: $CHROMEDRIVER_VERSION" && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/bin/ && \
    chmod +x /usr/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Clean up
RUN apt-get clean

# Copy application files
COPY requirements.txt .
COPY app.py .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Run the app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]