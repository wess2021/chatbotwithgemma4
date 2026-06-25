import os
import json
import requests
import time
from typing import Dict, Any, List, Optional

class OpenRouterService:
    """OpenRouter API service for accessing multiple AI models"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize OpenRouter service
        
        Args:
            api_key: OpenRouter API key (sk-or-v1-...)
            model: Model to use - defaults to Gemma 4 31B
        """
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        # Use configured model or default to Gemma 4 31B
        self.model = model or os.environ.get('OPENROUTER_MODEL', 'google/gemma-4-31b-it:free')
        self.base_url = "https://openrouter.ai/api/v1"
        self.conversation_history = []
        self.last_request_time = 0
        self.min_request_interval = 1  # seconds between requests
        
        # Track which models are available
        self.available_models = self._get_available_models()
        
        print(f"✅ OpenRouter initialized with model: {self.model}")
        print(f"📚 Using free model from Google: Gemma 4")
    
    def _get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                return [m.get('id') for m in models if m.get('id')]
            return []
        except Exception as e:
            print(f"⚠️  Could not fetch models: {e}")
            return []
    
    def send_message(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Send a message to OpenRouter and get response"""
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
            
            # Prepare messages
            messages = []
            
            # System prompt
            system_prompt = """You are an AI assistant for an e-commerce website. 
            Your role is to help customers with:
            1. Product information and recommendations
            2. Order tracking and status
            3. Shipping and delivery questions
            4. Returns and refunds
            5. General customer support
            
            Be friendly, professional, and helpful. Keep responses concise but informative.
            If you don't know something, be honest and suggest contacting customer support.
            Respond in the same language as the user's question."""
            
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
            # Add conversation history (last 10 messages)
            for msg in self.conversation_history[-10:]:
                messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })
            
            # Add current message
            full_message = message
            if context:
                full_message = f"Context: {json.dumps(context, ensure_ascii=False)}\nUser: {message}"
            
            messages.append({
                "role": "user",
                "content": full_message
            })
            
            # Prepare request
            url = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": os.environ.get('SITE_URL', 'http://localhost:5000'),
                "X-Title": "E-Commerce Chatbot"
            }
            
            # Make request
            response = requests.post(url, json=payload, headers=headers)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    bot_response = result['choices'][0]['message']['content']
                    
                    # Store in history
                    self.conversation_history.append({
                        'role': 'user',
                        'content': message
                    })
                    self.conversation_history.append({
                        'role': 'assistant',
                        'content': bot_response
                    })
                    
                    return {
                        'success': True,
                        'response': bot_response,
                        'model': self.model,
                        'usage': result.get('usage', {}),
                        'intent': self._extract_intent(bot_response),
                        'confidence': 0.85
                    }
                else:
                    return {
                        'success': False,
                        'response': "I didn't understand that. Could you please rephrase?",
                        'intent': 'error'
                    }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', str(response.status_code))
                print(f"❌ OpenRouter Error ({response.status_code}): {error_msg}")
                
                # If model not found, try fallback
                if response.status_code == 404:
                    return self._try_fallback_model(message)
                else:
                    return {
                        'success': False,
                        'response': self._get_fallback_response(message),
                        'intent': 'fallback'
                    }
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return {
                'success': False,
                'response': self._get_fallback_response(message),
                'intent': 'fallback'
            }
    
    def _try_fallback_model(self, message: str) -> Dict[str, Any]:
        """Try fallback models if primary fails"""
        fallback_models = [
            "google/gemma-4-26b-a4b-it:free",
            "openrouter/free",
            "qwen/qwen3-coder:free",
            "liquid/lfm-2.5-1.2b-instruct:free"
        ]
        
        original_model = self.model
        
        for fallback in fallback_models:
            if fallback != original_model:
                print(f"🔄 Trying fallback model: {fallback}")
                self.model = fallback
                result = self.send_message(message)
                self.model = original_model
                
                if result.get('success'):
                    result['response'] = result['response']
                    return result
        
        self.model = original_model
        return {
            'success': False,
            'response': self._get_fallback_response(message),
            'intent': 'fallback'
        }
    
    def _extract_intent(self, response: str) -> str:
        """Extract intent from response"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['product', 'item', 'buy', 'purchase']):
            return 'product_query'
        elif any(word in response_lower for word in ['order', 'track', 'delivery']):
            return 'order_query'
        elif any(word in response_lower for word in ['return', 'refund', 'exchange']):
            return 'return_query'
        elif any(word in response_lower for word in ['shipping', 'ship']):
            return 'shipping_query'
        else:
            return 'general_query'
    
    def _get_fallback_response(self, message: str) -> str:
        """Fallback responses when API fails"""
        message_lower = message.lower()
        
        responses = {
            'bonjour': "Bonjour! Comment puis-je vous aider aujourd'hui?",
            'hello': "Hello! How can I help you today?",
            'hi': "Hi there! What can I do for you?",
            'help': "I'm here to assist you. What do you need help with?",
            'product': "We have many great products. What are you looking for?",
            'order': "I can help with order inquiries. Do you have an order number?",
            'price': "Our prices are competitive. Which product interests you?",
            'thanks': "You're welcome! Anything else I can help with?",
            'bye': "Goodbye! Have a great day!",
            'merci': "De rien! Heureux de vous aider!"
        }
        
        for key, response in responses.items():
            if key in message_lower:
                return response
        
        return "I'm here to help! Could you please provide more details about what you need?"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️  Conversation history cleared")
    
    def switch_model(self, new_model: str) -> bool:
        """Switch to a different model"""
        try:
            # Validate model exists
            if new_model in self.available_models:
                self.model = new_model
                print(f"✅ Switched to model: {new_model}")
                return True
            else:
                print(f"⚠️  Model '{new_model}' not in available list. Trying anyway...")
                self.model = new_model
                return True
        except Exception as e:
            print(f"❌ Failed to switch model: {e}")
            return False
    
    def list_models(self) -> List[Dict]:
        """Get list of available models"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            return []
        except Exception as e:
            print(f"❌ Error fetching models: {e}")
            return []