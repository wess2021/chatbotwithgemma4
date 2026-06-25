import os
import requests
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    """List all available models from OpenRouter"""
    
    api_key = os.environ.get('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])
            
            print(f"📚 Found {len(models)} models\n")
            print("="*60)
            print("FREE MODELS (Recommended):")
            print("="*60)
            
            # Filter free models
            free_models = [
                m for m in models 
                if m.get('pricing', {}).get('prompt', '0') == '0'
                and 'free' in m.get('id', '').lower()
            ]
            
            # Also show Google models
            google_models = [
                m for m in models 
                if 'google' in m.get('id', '').lower()
            ]
            
            # Show free models
            for model in free_models[:20]:
                model_id = model.get('id')
                name = model.get('name', model_id)
                print(f"  ✅ {model_id}")
                print(f"     Name: {name}")
                print()
            
            print("="*60)
            print("GOOGLE MODELS:")
            print("="*60)
            
            for model in google_models[:10]:
                model_id = model.get('id')
                name = model.get('name', model_id)
                pricing = model.get('pricing', {})
                prompt_price = pricing.get('prompt', '0')
                completion_price = pricing.get('completion', '0')
                print(f"  📌 {model_id}")
                print(f"     Name: {name}")
                print(f"     Pricing: ${prompt_price}/1K prompt, ${completion_price}/1K completion")
                print()
            
            return models
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text[:200])
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    list_available_models()