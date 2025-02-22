# Mega Account Generator

An automated tool that creates Mega.nz accounts using temporary email addresses. The project includes a Flask web interface and uses Selenium for browser automation.

## Features

- Automated Mega.nz account creation
- Temporary email generation using MailTemp API
- Automatic email verification
- Web interface for account generation
- Account details saved to local files
- Detailed logging system

## Prerequisites

- Python 3.x
- Chrome browser
- ChromeDriver

## Dependencies

```
Flask==3.1.0
Requests==2.32.3
selenium==4.29.0
```

## Installation

1. Clone the repository:


2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Make sure ChromeDriver is installed and in your system PATH

## Configuration

The application uses the following configuration:
- MailTemp API endpoint: `https://mailtemp-production.up.railway.app/`
- Default password for generated accounts: `Study@123`
- Default wait time for email confirmation: 5 minutes

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Click the generate account button through the web interface

4. Account details will be saved in a text file with format `mega_account_<timestamp>.txt`

## Using the API

### Python Example

Here's a sample Python script that demonstrates how to use the API to generate a Mega account:

```python
import requests
import time
import json

def generate_mega_account():
    # API endpoint
    url = "http://localhost:5000/generate_account"
    
    try:
        # Send request to generate account
        response = requests.post(url)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Parse response
        result = response.json()
        
        if result['status'] == 'success':
            print("Account generated successfully!")
            print(f"Email: {result['account']['email']}")
            print(f"Password: {result['account']['password']}")
            return result['account']
        else:
            print(f"Error: {result['message']}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse response: {str(e)}")
        return None

def main():
    print("Generating Mega.nz account...")
    account = generate_mega_account()
    
    if account:
        # Save account details to file
        timestamp = int(time.time())
        filename = f"mega_account_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"Email: {account['email']}\n")
            f.write(f"Password: {account['password']}\n")
        
        print(f"Account details saved to {filename}")

if __name__ == "__main__":
    main()
```

### Using the Script

1. Save the above code as `generate_account.py`
2. Make sure the Mega Account Generator server is running
3. Run the script:
```bash
python generate_account.py
```

The script will:
- Send a request to generate a new account
- Display the account details in the console
- Save the account details to a text file
- Handle potential errors and provide appropriate feedback

## API Endpoints

- `GET /`: Renders the main web interface
- `POST /generate_account`: Generates a new Mega.nz account and returns the credentials

## Response Format

Successful response:
```json
{
    "status": "success",
    "account": {
        "email": "generated_email@example.com",
        "password": "Study@123"
    }
}
```

Error response:
```json
{
    "status": "error",
    "message": "Error details"
}
```

## Error Handling

The application includes comprehensive error handling for:
- Failed email generation
- Email verification timeout
- Invalid confirmation links
- Browser automation issues

## Logging

Logging is configured to output detailed debug information with timestamps and log levels.

## Security Considerations

- The application runs Chrome in headless mode by default
- Passwords are hardcoded for demonstration purposes - consider implementing secure password generation
- API endpoints should be properly secured in production

## Limitations

- Account creation may fail if Mega.nz changes their website structure
- Depends on external MailTemp API service availability
- Rate limiting may apply from Mega.nz or MailTemp services

## Contributing

Please feel free to submit issues and pull requests.

## License

[Your chosen license]

## Disclaimer

This tool is for educational purposes only. Please ensure compliance with Mega.nz's terms of service when using this tool.