import os
import traceback
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from helper.utils import toolset, logger

# Load environment variables
load_dotenv()

LOGGER_SERVICE = 'composio'
LOGGER_INTEGRATION = 'composio logs'

print("Testing direct email send via Composio...\n")

# Get connected accounts
accounts = toolset.get_connected_accounts()
print(f"Connected accounts: {len(accounts)}")

if not accounts:
    print("❌ No Gmail account connected!")
    exit(1)

print(f"✅ Using connected account\n")

# Find the GMAIL_SEND_EMAIL action
print("Searching for GMAIL_SEND_EMAIL action...")
actions = toolset.find_actions_by_tags(tags=["send_email"])
print(f"Found {len(actions)} send_email actions\n")

# Execute the send email action directly
try:
    print("Sending email directly via Composio...")
    logger(LOGGER_SERVICE, LOGGER_INTEGRATION, "INFO", "null", "Sending email directly via Composio")
    result = toolset.execute_action(
        action="GMAIL_SEND_EMAIL",
        params={
            "recipient_email": "madhurprakash2005@gmail.com",
            "subject": "Direct Test from Composio",
            "body": "This is a direct test email sent via Composio without Gemini"
        }
    )
    logger(LOGGER_SERVICE, LOGGER_INTEGRATION, "INFO", "null", "Email sent successfully via Composio")
    print(f"✅ Email sent successfully!")
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Error: {e}")
    traceback_error = traceback.print_exc()
    logger(LOGGER_SERVICE, LOGGER_INTEGRATION, "ERROR", "high", f"Error sending email via Composio: {traceback_error}")
    print("Failed to send email via Composio.")
