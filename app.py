from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import logging
import subprocess
import zipfile
import shutil
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Account model for the database
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

### Temporary Email Functions
def get_temp_email():
    """Generate a temporary email address using Guerrilla Mail API."""
    response = requests.get("https://api.guerrillamail.com/ajax.php?f=get_email_address")
    data = response.json()
    email = data['email_addr']
    sid_token = data['sid_token']
    logger.info(f"Generated temporary email: {email}")
    return email, sid_token

def check_inbox(sid_token):
    """Check the inbox for new emails using the Guerrilla Mail API."""
    response = requests.get(f"https://api.guerrillamail.com/ajax.php?f=check_email&sid_token={sid_token}&seq=0")
    data = response.json()
    return data['list']

def fetch_email(sid_token, email_id):
    """Fetch the content of a specific email."""
    response = requests.get(f"https://api.guerrillamail.com/ajax.php?f=fetch_email&sid_token={sid_token}&email_id={email_id}")
    data = response.json()
    return data['mail_body']

### Chrome and ChromeDriver Setup
def find_chrome_binary():
    """Dynamically locate the Chrome binary on the system."""
    possible_paths = [
        "/usr/bin/google-chrome",           # Default Linux
        "/usr/lib/chromium-browser/chrome", # Chromium alternative
        "/usr/bin/google-chrome-stable",    # Some Linux distros
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Windows
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",  # Windows 32-bit
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # macOS
    ]
    
    # Check environment variable first
    chrome_binary = os.getenv("CHROME_BINARY")
    if chrome_binary and os.path.exists(chrome_binary):
        logger.info(f"Using Chrome binary from CHROME_BINARY: {chrome_binary}")
        return chrome_binary
    
    # Try common locations
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found Chrome binary at: {path}")
            return path
    
    # Try system PATH
    try:
        chrome_path = shutil.which("google-chrome") or shutil.which("chrome")
        if chrome_path:
            logger.info(f"Found Chrome in PATH: {chrome_path}")
            return chrome_path
    except Exception:
        pass
    
    raise Exception("Google Chrome not found in common locations or PATH")

def get_chrome_version(chrome_binary):
    """Get the installed Chrome version using the binary."""
    try:
        cmd = [chrome_binary, "--version"]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        version = re.search(r"Google Chrome (\d+\.\d+\.\d+\.\d+)", output).group(1)
        logger.info(f"Detected Chrome version: {version}")
        return version
    except Exception as e:
        logger.error(f"Failed to detect Chrome version with {chrome_binary}: {e}")
        raise Exception(f"Could not determine Chrome version: {str(e)}")

def download_chromedriver(chrome_version):
    """Download ChromeDriver matching the Chrome version."""
    base_version = chrome_version.split('.')[0]  # Major version only
    url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{base_version}"
    latest_version = requests.get(url).text.strip()
    
    download_url = f"https://chromedriver.storage.googleapis.com/{latest_version}/chromedriver_{'win32' if os.name == 'nt' else 'linux64'}.zip"
    chromedriver_zip = "chromedriver.zip"
    
    logger.info(f"Downloading ChromeDriver version {latest_version} from {download_url}")
    response = requests.get(download_url)
    with open(chromedriver_zip, 'wb') as f:
        f.write(response.content)
    
    with zipfile.ZipFile(chromedriver_zip, 'r') as zip_ref:
        zip_ref.extractall(".")
    
    chromedriver_path = "./chromedriver.exe" if os.name == 'nt' else "./chromedriver"
    os.chmod(chromedriver_path, 0o755) if os.name != 'nt' else None  # Make executable on non-Windows
    os.remove(chromedriver_zip)
    logger.info(f"ChromeDriver downloaded and extracted to {chromedriver_path}")
    return chromedriver_path

def create越し():
    """Create a headless Chrome browser instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Locate Chrome binary
    chrome_binary = find_chrome_binary()
    options.binary_location = chrome_binary
    
    # Check for ChromeDriver or download it
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")
    if not os.path.exists(chromedriver_path):
        logger.warning(f"ChromeDriver not found at {chromedriver_path}, attempting to download...")
        chrome_version = get_chrome_version(chrome_binary)
        chromedriver_path = download_chromedriver(chrome_version)
    
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    logger.info("Headless Chrome browser initialized")
    return driver

### Mega.nz Account Creation Functions
def register_mega(driver, email):
    """Register a new account on Mega.nz using Selenium."""
    driver.get("https://mega.nz/register")
    time.sleep(2)  # Wait for page to load

    driver.find_element(By.XPATH, "//input[@placeholder='First name']").send_keys("King")
    driver.find_element(By.XPATH, "//input[@placeholder='Last name']").send_keys("Singh")
    driver.find_element(By.XPATH, "//input[@placeholder='Email address']").send_keys(email)
    driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys("Study@123")
    driver.find_element(By.XPATH, "//input[@placeholder='Retype password']").send_keys("Study@123")
    
    driver.find_element(By.XPATH, "//input[@type='checkbox']").click()
    driver.find_element(By.CLASS_NAME, "register-button").click()
    time.sleep(5)  # Wait for registration to process
    logger.info("Mega.nz registration submitted")

def wait_for_confirmation_email(sid_token, max_wait=300, poll_interval=10):
    """Wait for and extract the confirmation link from the Mega.nz email."""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        emails = check_inbox(sid_token)
        for email in emails:
            if email['mail_from'] == "welcome@mega.nz":
                email_body = fetch_email(sid_token, email['mail_id'])
                match = re.search(r"https://mega\.nz/#confirm\w+", email_body)
                if match:
                    logger.info(f"Confirmation link found: {match.group(0)}")
                    return match.group(0)
        time.sleep(poll_interval)
    raise Exception("Confirmation email not received within time limit")

def confirm_account(driver, confirm_link):
    """Confirm the Mega.nz account using the confirmation link."""
    driver.get(confirm_link)
    time.sleep(2)  # Wait for page to load
    
    driver.find_element(By.ID, "login-password2").send_keys("Study@123")
    driver.find_element(By.CLASS_NAME, "login-button").click()
    time.sleep(5)  # Wait for confirmation to complete
    logger.info("Account confirmed")

def save_account(email, password):
    """Save the created account details to the database."""
    account = Account(email=email, password=password)
    db.session.add(account)
    db.session.commit()
    logger.info(f"Account saved: {email}")

def create_mega_account():
    """Orchestrate the Mega.nz account creation process."""
    driver = create_browser()
    try:
        email, sid_token = get_temp_email()
        register_mega(driver, email)
        confirm_link = wait_for_confirmation_email(sid_token)
        confirm_account(driver, confirm_link)
        save_account(email, "Study@123")
        return email, "Study@123"
    except Exception as e:
        logger.error(f"Error in account creation: {str(e)}")
        raise
    finally:
        driver.quit()

### Flask Routes
@app.route('/create_account', methods=['POST'])
def create_account_route():
    """API endpoint to create a new Mega.nz account."""
    try:
        email, password = create_mega_account()
        return jsonify({'status': 'success', 'email': email, 'password': password})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/accounts', methods=['GET'])
def list_accounts():
    """API endpoint to list all created accounts."""
    accounts = Account.query.all()
    return jsonify({'accounts': [{'email': acc.email, 'password': acc.password} for acc in accounts]})

@app.route('/')
def index():
    """Web interface for creating Mega.nz accounts."""
    return '''
    <html>
    <body>
        <h1>Mega.nz Account Creator</h1>
        <button onclick="createAccount()">Create New Account</button>
        <div id="result"></div>
        <script>
            function createAccount() {
                document.getElementById('result').innerText = 'Creating account, please wait...';
                fetch('/create_account', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            document.getElementById('result').innerText = 
                                `Account created: ${data.email} (Password: ${data.password})`;
                        } else {
                            document.getElementById('result').innerText = 
                                `Error: ${data.message}`;
                        }
                    })
                    .catch(error => {
                        document.getElementById('result').innerText = 
                            `Network error: ${error.message}`;
                    });
            }
        </script>
    </body>
    </html>
    '''

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
