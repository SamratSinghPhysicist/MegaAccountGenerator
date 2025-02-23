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

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Temporary Email Service API Configuration
API_MAIN_DOMAIN = "https://mailtemp-production.up.railway.app/"
BASE_URL = f"{API_MAIN_DOMAIN}api"

def create_temp_email():
    """Create a temporary email address using the MailTemp API"""
    logging.debug("Creating temporary email...")
    response = requests.post(f"{BASE_URL}/email")
    if response.status_code == 200:
        data = response.json()
        logging.debug(f"Email created: {data['address']}")
        return data
    else:
        logging.error(f"Email creation failed: {response.json().get('details', 'No details')}")
        raise Exception(f"Failed to create email: {response.json()['message']}")

def get_messages(email_id):
    """Get messages for a specific email ID using the MailTemp API"""
    logging.debug(f"Fetching messages for email ID: {email_id}")
    response = requests.get(f"{BASE_URL}/email/{email_id}/messages")
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to get messages: {response.json().get('message', 'Unknown error')}")

def wait_for_confirmation_email(email_id):
    """Poll for the Mega.nz confirmation email"""
    logging.debug("Waiting for confirmation email...")
    for _ in range(30):  # Wait up to 5 minutes
        messages = get_messages(email_id)
        for message in messages:
            if message['from'] == "welcome@mega.nz":
                content = message['content']
                if isinstance(content, list):
                    content = " ".join(str(item) for item in content)
                elif not isinstance(content, str):
                    content = str(content)
                logging.debug("Confirmation email received.")
                return content
        time.sleep(10)
    raise Exception("Confirmation email not received within 5 minutes")

def extract_confirm_link(email_content):
    """Extract the confirmation link from the email content"""
    if not isinstance(email_content, str):
        raise Exception(f"Invalid email content type: {type(email_content)}. Expected string.")
    match = re.search(r'https://mega\.nz/#confirm\w+', email_content)
    if match:
        logging.debug(f"Confirmation link extracted: {match.group(0)}")
        return match.group(0)
    raise Exception("Confirmation link not found in email content:\n" + email_content[:500])

def create_mega_account():
    email_data = create_temp_email()
    temp_email = email_data['address']
    email_id = email_data['id']

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"  # Render.com's Chromium path

    try:
        # Use webdriver_manager with Chromium explicitly
        logging.debug("Setting up ChromeDriver with webdriver_manager...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options = options)
        # driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)
        logging.debug("ChromeDriver initialized successfully.")



        # Step 1: Open registration page
        driver.get("https://mega.nz/register")

        # Step 2: Fill registration form
        # First name
        wait.until(EC.visibility_of_element_located(
            (By.ID, "register-firstname-registerpage2")
        )).send_keys("KingSingh")

        # Last name
        driver.find_element(By.ID, "register-lastname-registerpage2").send_keys("SamSingh")

        # Email
        driver.find_element(By.ID, "register-email-registerpage2").send_keys(temp_email)

        # Password field
        password_field = wait.until(EC.visibility_of_element_located(
            (By.ID, "register-password-registerpage2")
        ))
        password_field.click()  # Focus the field to trigger any JS
        password_field.send_keys("Study@123")

        time.sleep(1)

        # Retype password field
        retype_password_field = wait.until(EC.visibility_of_element_located(
            (By.ID, "register-password-registerpage3")
        ))
        retype_password_field.click()  # Focus the field
        time.sleep(1)
        retype_password_field.send_keys("Study@123")

        time.sleep(1)
        # Step 3: Check terms checkbox if not already checked
        driver.find_element(By.XPATH, "//input[@type='checkbox' and @tabindex='6']").click()

        time.sleep(1)

        driver.find_element(By.XPATH, "//input[@type='checkbox' and @tabindex='7']").click()

        time.sleep(1)

        # Step 4: Click Sign Up
        sign_up_button = wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "register-button")
        ))
        sign_up_button.click()

        # Step 5: Wait for confirmation email
        email_content = wait_for_confirmation_email(email_id)
        confirm_link = extract_confirm_link(email_content)
        logging.debug("Navigating to confirmation link...")
        time.sleep(5)
        driver.get(confirm_link)
        
        # Step 6: Confirm account
        logging.debug("Entering confirmation password...")
        time.sleep(5)
        wait.until(EC.presence_of_element_located(
            (By.ID, "login-password2")
        )).send_keys("Study@123")
        driver.find_element(By.CLASS_NAME, "login-button").click()

        # Step 7: Wait for account to be active
        logging.debug("Waiting for account activation...")
        time.sleep(10)
        driver.get("https://mega.nz/")
        time.sleep(10)

        # Step 8: Save account details
        account_details = {"email": temp_email, "password": "Study@123"}
        with open(f"mega_account_{int(time.time())}.txt", "w") as f:
            f.write(f"Email: {temp_email}\nPassword: Study@123\n")

        return account_details

    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        raise Exception(f"Account creation failed: {str(e)}")
    finally:
        driver.quit()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_account', methods=['POST'])
def generate_account():
    try:
        account_details = create_mega_account()
        return jsonify({"status": "success", "account": account_details})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
