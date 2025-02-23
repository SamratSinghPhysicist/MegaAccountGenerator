# Use cypress/browser:latest as the base image (includes Chromium and dependencies)
FROM cypress/browser:latest

#Downloading Chrome
sudo apt-get purge google-chrome-stable
sudo wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_97.0.4692.71-1_amd64.deb && \
sudo dpkg -i google-chrome-stable_97.0.4692.71-1_amd64.deb && \
sudo apt-mark hold google-chrome-stable

wget https://chromedriver.storage.googleapis.com/97.0.4692.71/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip chromedriver -d /usr/local/bin

# Set the port as an argument (default to 5000 for Flask compatibility with Render.com)
ARG PORT=5000
ENV PORT=$PORT

# Install Python 3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Expose the port
EXPOSE $PORT

# Command to run the Flask app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:${PORT}", "--workers", "1", "--timeout", "600"]