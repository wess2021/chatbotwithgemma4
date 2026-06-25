import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("="*50)
print("Testing .env Loading")
print("="*50)

# Try to get the key
api_key = os.environ.get('OPENROUTER_API_KEY')

if api_key:
    print(f"✅ OPENROUTER_API_KEY found!")
    print(f"   Key: {api_key[:15]}...{api_key[-10:]}")
    print(f"   Length: {len(api_key)} characters")
else:
    print("❌ OPENROUTER_API_KEY NOT found!")

# Also check other variables
print(f"\n📝 FLASK_APP: {os.environ.get('FLASK_APP')}")
print(f"📝 DEBUG: {os.environ.get('DEBUG')}")
print(f"📝 OPENROUTER_MODEL: {os.environ.get('OPENROUTER_MODEL')}")

# Check the actual .env file path
env_path = os.path.join(os.getcwd(), '.env')
print(f"\n📁 .env file path: {env_path}")
print(f"📁 File exists: {os.path.exists(env_path)}")