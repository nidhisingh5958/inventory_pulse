#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_groq():
    print("🧪 Testing Groq Integration")
    print("=" * 30)
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env")
        return False
    
    print("✅ Groq API key found")
    
    try:
        # Initialize Groq client
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized")
        
        # Test API call
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{
                "role": "user", 
                "content": "Analyze inventory: Item=Paper, Stock=50, Daily_Usage=10. Return JSON with days_until_depletion."
            }],
            temperature=0.2,
            max_tokens=512
        )
        
        print("✅ Groq API call successful")
        print(f"Response: {response.choices[0].message.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Groq test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_groq()