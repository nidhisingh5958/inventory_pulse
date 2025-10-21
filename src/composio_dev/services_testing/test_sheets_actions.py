import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from helper.utils import toolset
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Try different action names to find which one works
action_attempts = [
    ("GOOGLESHEETS_BATCH_UPDATE", {
        "spreadsheet_id": SPREADSHEET_ID,
        "sheet_name": "Sheet1",
        "range": "D3",
        "values": [[100]]
    }),
    ("GOOGLESHEETS_BATCH_UPDATE", {
        "spreadsheet_id": SPREADSHEET_ID,
        "sheet_name": "Sheet1",
        "data": [{
            "range": "D3",
            "values": [[100]]
        }]
    }),
]

print(f"Testing Google Sheets actions on spreadsheet: {SPREADSHEET_ID}\n")

for action_name, params in action_attempts:
    print(f"Trying action: {action_name}")
    try:
        result = toolset.execute_action(action=action_name, params=params)
        print(f"✅ SUCCESS with {action_name}!")
        print(f"Result: {result}\n")
        break
    except Exception as e:
        print(f"❌ Failed: {str(e)[:200]}\n")

print("\nTrying to get spreadsheet metadata to see structure...")
try:
    result = toolset.execute_action(
        action="GOOGLESHEETS_GET_SPREADSHEET",
        params={"spreadsheet_id": SPREADSHEET_ID}
    )
    print(f"✅ Get spreadsheet metadata works!")
    if result.get("data"):
        sheets = result.get("data", {}).get("sheets", [])
        print(f"Found {len(sheets)} sheets")
except Exception as e:
    print(f"❌ Failed: {str(e)[:200]}")
