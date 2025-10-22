import asyncio
import json
import traceback
from composio import ComposioToolSet, App
import os
from dotenv import load_dotenv
import requests
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from google import genai
from composio_gemini import GeminiProvider
from config.redis_cofig import redis_client
from google.genai import types


load_dotenv()

# Create composio toolset with user authentication
USER_ID = os.getenv("COMPOSIO_USER_ID", "default-user")  # Use a unique user ID for your app
toolset = ComposioToolSet(entity_id=USER_ID)

LOGGER_SERVICE = 'composio'
LOGGER_INTEGRATION = 'composio logs'

# Auth Config ID from your Composio dashboard
# You should have created this in the Composio dashboard for Gmail
COMPOSIO_GMAIL_ACCOUNT_ID = os.getenv("COMPOSIO_GMAIL_ACCOUNT_ID", "YOUR_COMPOSIO_GMAIL_ACCOUNT_ID")

connected = False

def check_gmail_connection():
    try:
        accounts = toolset.get_connected_accounts()
        if accounts:
            print(f"Found {len(accounts)} existing connection(s)")
            connected = True
        else:
            print("No connected accounts found. Need to authenticate with Gmail...")
    except Exception as e:
        print(f"Could not retrieve connected accounts: {e}")

    # If not connected, initiate OAuth flow
    if not connected and COMPOSIO_GMAIL_ACCOUNT_ID != "your_auth_config_id":
        try:
            print("\nInitiating Gmail OAuth flow...")
            connection_request = toolset.initiate_connection(
                app=App.GMAIL,
                integration_id=COMPOSIO_GMAIL_ACCOUNT_ID,
            )
            print(f"\n🔗 Please visit this link to authorize Gmail:\n{connection_request.redirect_url}\n")
            print("Waiting for authorization...")
            print(f"✅ Gmail connected successfully!")
            connected = True
        except Exception as e:
            print(f"Failed to connect Gmail: {e}")
    else:
        if COMPOSIO_GMAIL_ACCOUNT_ID == "your_auth_config_id":
            print("\n⚠️  GMAIL_AUTH_CONFIG_ID not set in .env file!")
            print("Please:")
            print("1. Go to https://platform.composio.dev/auth-configs")
            print("2. Create a Gmail OAuth2 auth config")
            print("3. Add GMAIL_AUTH_CONFIG_ID=<your_id> to .env")
            connected = False


# Create google client
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize GeminiProvider to wrap tools
provider = GeminiProvider()

# Define tool executor callback that uses authenticated connections
def execute_tool(tool_name: str, tool_input: dict) -> str:
    check_gmail_connection()
    """Execute tool using Composio with authenticated account"""
    if not connected:
        return "Gmail account not connected. Please authenticate first by running with GMAIL_AUTH_CONFIG_ID set."
    
    action_name = tool_name.upper()
    try:
        result = toolset.execute_action(
            action=action_name,
            params=tool_input,
        )
        return str(result)
    except Exception as e:
        return f"Error executing {action_name}: {str(e)}"
    

# Get action schemas for Gmail send email
actions = toolset.find_actions_by_tags(tags=["send_email"])

# Wrap the action schemas for Gemini with execute_tool callback
tools = provider.wrap_tools(actions, execute_tool=execute_tool)

# Create genai client config with wrapped tools
config = types.GenerateContentConfig(tools=tools)

# Use the chat interface.
chat = gemini_client.chats.create(model="gemini-2.0-flash", config=config)

    
def gemini_draft_email(recipient_email: str, context: str):

    # Send message asking Gemini to send an email with correct parameter names
    response = chat.send_message(f"""
Your task is to draft a professional email based on the context provided., the context is: {context}
Send an email using GMAIL_SEND_EMAIL action with these parameters:
- recipient_email: {recipient_email}
- subject: {context}
- body: {context}

and provide only the response in JSON format as this response model: {{
    "recipient_email": "{recipient_email}", 
    "subject": "Subject based on context", 
    "body": "Drafted email body based on context"
}}""")
    
    print("type of response.text:", type(response.text))
    return response.text

def convert_string_to_json(json_string: str):
    try:
        print("received json_string:", json_string)
        if json_string.startswith("```"):
            json_string = json_string.strip("`")   # Remove leading/trailing backticks
            json_string = json_string.replace("json", "", 1).strip()  # Remove 'json' tag
        json_object = json.loads(json_string)
        print("="*60)
        print("="*60)
        print("Converted JSON object:", json_object)
        return json_object
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON string: {e}")
        return None
    
# ✅ Background listener function
async def redis_listener():
    """Continuously listen for Redis messages"""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("low_stock_alerts")
    print("✅ Subscribed to low_stock_alerts channel...")

    while True:
        try:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)

            if msg is None:
                await asyncio.sleep(0.1)  # Prevent CPU spinning
                continue

            print(f"📥 Raw Redis message: {msg}")
            alert_data = json.loads(msg["data"])
            print(f"Parsed Alert Data: {alert_data}")

            print("✉️ Invoking Gemini draft email function...")
            res = gemini_draft_email(
                recipient_email=alert_data["email"],
                context=(
                    f"I am running low on stocks, draft an email to my supplier {alert_data['supplier']}.\n"
                    f"Current stock left: {alert_data['new_stock_left']} units, "
                    f"Daily demand: {alert_data['demand']} units. "
                    "Request to replenish as soon as possible."
                )
            )
            print(f"Draft email: {res}")
            json_res = convert_string_to_json(res)
            print("type of json_res:", type(json_res))

            if json_res is None:
                print("❌ AI response is not valid JSON, skipping email send.")
                return {"status": "error", "message": "AI response is not valid JSON."}

            try:
                print("📨 Sending email via Composio...")
                result = toolset.execute_action(
                    action="GMAIL_SEND_EMAIL",
                    params={
                        "recipient_email": json_res['recipient_email'],
                        "subject": json_res['subject'],
                        "body": json_res['body']
                    }
                )
                print("✅ Email sent successfully!")

            except Exception as e:
                print(f"❌ Error while sending email: {e}")
                traceback.print_exc()

        except asyncio.CancelledError:
            print("❗ Listener task cancelled.")
            break
        except Exception as e:
            print(f"❌ Error in listener: {e}")
            traceback.print_exc()
            await asyncio.sleep(1)  # Wait before retrying