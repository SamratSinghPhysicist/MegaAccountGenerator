# Deploying Mega Account Generator to Render.com

## 1. Project Structure
First, ensure your project structure looks like this:
```
mega-account-generator/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── build.sh
└── .gitignore
```

## 2. Update Requirements
Create/update `requirements.txt` with these dependencies:

```
Flask==3.1.0
Requests==2.32.3
selenium==4.29.0
webdriver_manager==4.0.1
gunicorn==21.2.0
```

## 3. Create build.sh
Create a `build.sh` file with the following content:

```bash
#!/usr/bin/env bash
# Exit on error
set -e

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update -y
apt-get install -y google-chrome-stable

# Install Python dependencies
pip install -r requirements.txt
```

## 4. Modify app.py
Update your `app.py` to use webdriver_manager and handle Render.com's environment:

```python
import requests
import time
import re
import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from flask import Flask, jsonify, render_template, request

# Rest of your imports...

def create_mega_account():
    email_data = create_temp_email()
    temp_email = email_data['address']
    email_id = email_data['id']

    # Updated Chrome options for Render.com
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.binary_location = "/usr/bin/google-chrome"  # Chrome binary path on Render.com

    # Use webdriver_manager to handle ChromeDriver installation
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)

    # Rest of your create_mega_account function...

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
```

## 5. Create .gitignore
Create a `.gitignore` file:

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
*.log
mega_account_*.txt
```

## 6. Deploy to Render.com

1. Push your code to a GitHub repository

2. Go to Render.com and create a new Web Service:
   - Connect your GitHub repository
   - Choose the branch to deploy
   - Select "Python" as the runtime
   - Set the build command: `./build.sh`
   - Set the start command: `gunicorn app:app`

3. Configure Environment Variables (if needed):
   - `PORT`: Will be set automatically by Render
   - Add any other environment variables your app needs

4. Advanced Settings:
   - Set Instance Type: Choose based on your needs (minimum "Individual" plan recommended)
   - Health Check Path: `/`
   - Auto-Deploy: Enable if desired

## Environment Variables
Render.com will automatically set:
- `PORT`: The port your app should listen on
- `RENDER`: Set to `true` when running on Render

## Important Notes

1. **Chrome Installation**: The `build.sh` script automatically installs Chrome during deployment.

2. **Memory Usage**: Chrome in headless mode can be memory-intensive. Monitor your app's memory usage and adjust the instance type if needed.

3. **Timeouts**: Render has a 60-second timeout for incoming requests. Your account creation process might need to be adjusted to handle this limitation.

4. **File System**: Render's file system is ephemeral. Any saved account files will be lost when the instance restarts. Consider using a database or external storage service.

## Troubleshooting

1. If Chrome fails to start:
   - Check the logs in Render dashboard
   - Verify Chrome installation in build logs
   - Ensure all Chrome flags are properly set

2. If the app crashes:
   - Check memory usage
   - Review error logs
   - Verify all dependencies are properly installed

3. If requests timeout:
   - Consider implementing a queue system
   - Break down long operations
   - Use webhooks for lengthy processes

## Recommended Modifications

1. Consider implementing a database to store account details instead of files:
```python
# Example using SQLite
import sqlite3

def save_account_details(email, password):
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (email text, password text, created_date text)''')
    c.execute("INSERT INTO accounts VALUES (?,?,?)", 
              (email, password, time.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
```

2. Add rate limiting to prevent abuse:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/generate_account', methods=['POST'])
@limiter.limit("3 per hour")
def generate_account():
    # Your existing code...
```

## Monitoring

Monitor your application using Render's built-in metrics:
- Memory usage
- CPU usage
- Request latency
- Error rates

Consider adding additional monitoring using logging services like Sentry or LogDNA.
