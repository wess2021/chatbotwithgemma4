import os
import time
from dotenv import load_dotenv
import requests

load_dotenv()

def test_openrouter():
    """Test OpenRouter API with correct model names"""
    
    api_key = os.environ.get('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ No OPENROUTER_API_KEY found in .env")
        return False
    
    print(f"📝 Testing OpenRouter with key: {api_key[:15]}...")
    
    # Try models in order of reliability
    models_to_test = [
        "google/gemini-flash-1.5",  # Try this first
        "mistralai/mistral-7b-instruct:free",  # Very reliable
        "meta-llama/llama-3.2-3b-instruct:free",  # Also reliable
    ]
    
    for model in models_to_test:
        print(f"\n{'='*50}")
        print(f"Testing model: {model}")
        print('='*50)
        
        try:
            # Direct API test
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "Say 'Hello! This is a test!'"}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                print(f"✅ Model {model} is working!")
                print(f"Response: {content[:100]}...")
                return True
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"❌ Model {model} failed: {error_msg}")
                
                if response.status_code == 429:
                    print("   Rate limit hit. Waiting 3 seconds...")
                    time.sleep(3)
                
        except Exception as e:
            print(f"❌ Error with {model}: {e}")
    
    print("\n⚠️  All models failed. Let's try using fallback responses.")
    return False

def test_fallback():
    """Test fallback responses without API"""
    print("\n" + "="*50)
    print("Testing fallback responses")
    print('='*50)
    
    from app.services.openrouter_service import OpenRouterService
    
    # Create service without API (it will use fallback)
    try:
        service = OpenRouterService(api_key="dummy_key")
        
        test_messages = ["hello", "product", "order", "merci"]
        
        for msg in test_messages:
            result = service.send_message(msg)
            print(f"User: {msg}")
            print(f"Bot: {result.get('response')}")
            print("-" * 30)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing OpenRouter...")
    print("\nIf API fails, we'll use fallback responses.\n")
    
    success = test_openrouter()
    
    if not success:
        print("\n⚠️  API test failed. Testing fallback responses...")
        test_fallback()