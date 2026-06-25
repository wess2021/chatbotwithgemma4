import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_openrouter_key():
    """Check if OpenRouter API key is valid"""
    
    api_key = os.environ.get('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ No OPENROUTER_API_KEY found in .env")
        print("\n📝 To get your OpenRouter API key:")
        print("   1. Go to: https://openrouter.ai/account")
        print("   2. Sign in or create an account")
        print("   3. Click 'Create API Key'")
        print("   4. Copy the key (starts with 'sk-or-v1-')")
        print("   5. Add it to your .env file")
        return False
    
    print(f"📝 API Key found: {api_key[:15]}...")
    
    # Check key format
    if not api_key.startswith('sk-or-v1-'):
        print("⚠️  Your API key format doesn't match the expected format.")
        print("   OpenRouter keys should start with 'sk-or-v1-'")
        print("   Please get a new key from: https://openrouter.ai/account")
        return False
    
    # Test the key
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Try to list models (simple test)
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers
        )
        
        if response.status_code == 200:
            models = response.json()
            print("✅ API key is valid!")
            print(f"📚 Available models: {len(models.get('data', []))} found")
            return True
        elif response.status_code == 401:
            print("❌ Invalid API key!")
            print("   Please get a new key from: https://openrouter.ai/account")
            return False
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking API key: {e}")
        return False

if __name__ == "__main__":
    check_openrouter_key()