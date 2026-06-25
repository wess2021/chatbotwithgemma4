import google.generativeai as genai
import os
import json
from typing import List, Dict, Any

class GeminiService:
    """Google Gemini AI Service for chatbot - FREE version"""
    
    def __init__(self, api_key=None):
        """Initialize Gemini with API key"""
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required. Get it from: https://makersuite.google.com/app/apikey")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use the free model - gemini-pro is free
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = None
        self.conversation_history = []
        self.system_instruction_set = False
    
    def start_conversation(self):
        """Start a new conversation with Gemini"""
        try:
            # Start a new chat session
            self.chat = self.model.start_chat(history=[])
            self.conversation_history = []
            self.system_instruction_set = True
            
            # Send system prompt as first message (free)
            system_prompt = """
            You are an AI assistant for an e-commerce website. Your role is to help customers with:
            1. Product information and recommendations
            2. Order tracking and status
            3. Shipping and delivery questions
            4. Returns and refunds
            5. General customer support
            
            Be friendly, professional, and helpful. Keep responses concise but informative.
            """
            
            # This is free - the first message sets the context
            response = self.chat.send_message(system_prompt)
            return response.text
            
        except Exception as e:
            print(f"Error starting conversation: {e}")
            return "I'm ready to help you!"
    
    def send_message(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Send a message to Gemini and get response"""
        try:
            # If we don't have a chat session, start one
            if not self.chat:
                self.start_conversation()
            
            # Prepare the message with context if provided
            full_message = message
            if context:
                context_str = json.dumps(context, ensure_ascii=False)
                full_message = f"Context: {context_str}\nUser: {message}"
            
            # Send message to Gemini (FREE)
            response = self.chat.send_message(full_message)
            
            # Get the response text
            bot_response = response.text
            
            # Store in history
            self.conversation_history.append({
                'user': message,
                'bot': bot_response
            })
            
            # Extract intent (simplified)
            intent = self._extract_intent(bot_response)
            
            return {
                'success': True,
                'response': bot_response,
                'intent': intent,
                'confidence': 0.85
            }
            
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': "I apologize, but I'm having trouble responding right now. Please try again later."
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
        elif any(word in response_lower for word in ['hello', 'hi', 'hey']):
            return 'greeting'
        else:
            return 'general_query'
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        if self.chat:
            # Start fresh conversation
            self.start_conversation()