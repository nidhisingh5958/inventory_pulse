import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from helper.utils import gemini_draft_email
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    res = gemini_draft_email(
        recipient_email="recipient@example.com",
        context="I am running low on stocks of steel, draft an email to my supplier for the same, the email of my supplier is supplier@example.com."
    )

    print("\n" + "="*60)
    print("Gemini Draft Email Result:")
    print("="*60)
    print(res)