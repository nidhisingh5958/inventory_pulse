#!/usr/bin/env python3
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

def check_environment():
    required_vars = ["GROQ_API_KEY", "COMPOSIO_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ Environment variables configured")
    return True

def main():
    print("🚀 Inventory Replenishment Copilot")
    print("=" * 40)
    
    if not check_environment():
        print("Please update your .env file with required credentials.")
        return
    
    print("🌐 Starting server at http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()