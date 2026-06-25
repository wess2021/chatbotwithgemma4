import os
import json
import requests
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import random
import re
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup

# Import du scraper Nety.tn
from app.services.nety_scraper import scraper as nety_scraper

class OpenRouterService:
    """OpenRouter API service with Nety.tn scraping and quick replies"""
    
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
        
        # Full conversation history - stores ALL messages
        self.conversation_history = []
        self.conversation_metadata = {
            'started_at': datetime.now().isoformat(),
            'total_messages': 0,
            'user_messages': 0,
            'bot_messages': 0
        }
        
        self.last_request_time = 0
        self.min_request_interval = 1
        
        # Track which models are available
        self.available_models = self._get_available_models()
        
        # Intégrer le scraper Nety
        self.nety_scraper = nety_scraper
        
        # URLs des services Nety.tn pour les quick replies
        self.nety_urls = {
            'smartphones': 'https://www.nety.tn/fr/8-smartphones',
            'accessoires': 'https://www.nety.tn/fr/9-accessoires',
            'abonnement': 'https://www.nety.tn/fr/module/demandeabonnement/nouveau',
            'paiement': 'https://www.nety.tn/fr/module/paiementfacture/nouveau',
            'parrainage': 'https://www.nety.tn/fr/module/demandeparrainage/parrainage',
            'reclamation': 'https://www.nety.tn/fr/module/reclamation/ReclamationSearch',
            'contact': 'https://www.nety.tn/fr/contact'
        }
        
        print(f"✅ OpenRouter initialized with model: {self.model}")
        print(f"🛍️ Nety.tn scraper integrated with {len(self.nety_scraper.categories)} categories")
        print(f"🔗 Nety.tn services: {len(self.nety_urls)} URLs loaded")
    
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
            print(f"⚠️ Could not fetch models: {e}")
            return []
    
    # ============ SCRAPING METHODS ============
    
    def _search_nety_products(self, query: str, limit: int = 5) -> List[Dict]:
        """Rechercher des produits sur Nety.tn en utilisant le scraper"""
        try:
            products = self.nety_scraper.search_products(query, limit)
            return products
        except Exception as e:
            print(f"❌ Erreur scraping Nety: {e}")
            return []
    
    def _get_quick_replies(self, intent: str, products: List[Dict] = None) -> List[Dict]:
        """Générer des tickets (suggestions) pour guider l'utilisateur"""
        quick_replies = []
        
        if intent == 'product_query':
            if products:
                # Suggérer les premiers produits
                for product in products[:3]:
                    quick_replies.append({
                        'label': product.get('name', 'Produit')[:30],
                        'action': 'view_product',
                        'payload': {
                            'product_name': product.get('name'),
                            'product_link': product.get('link'),
                            'product_price': product.get('price')
                        }
                    })
                
                quick_replies.append({
                    'label': '🔍 Chercher autre chose',
                    'action': 'search',
                    'payload': {}
                })
            else:
                quick_replies = [
                    {'label': '📱 Smartphones', 'action': 'view_category', 'payload': {'url': self.nety_urls['smartphones'], 'name': 'Smartphones'}},
                    {'label': '🎧 Accessoires', 'action': 'view_category', 'payload': {'url': self.nety_urls['accessoires'], 'name': 'Accessoires'}},
                    {'label': '🔍 Chercher', 'action': 'search', 'payload': {}}
                ]
        
        elif intent == 'order_query':
            quick_replies = [
                {'label': '📦 Suivre commande', 'action': 'view_service', 'payload': {'url': self.nety_urls['paiement'], 'name': 'Paiement'}},
                {'label': '🔄 Réclamation', 'action': 'view_service', 'payload': {'url': self.nety_urls['reclamation'], 'name': 'Réclamation'}},
                {'label': '📱 Smartphones', 'action': 'view_category', 'payload': {'url': self.nety_urls['smartphones'], 'name': 'Smartphones'}}
            ]
        
        elif intent == 'return_query':
            quick_replies = [
                {'label': '🔄 Réclamation', 'action': 'view_service', 'payload': {'url': self.nety_urls['reclamation'], 'name': 'Réclamation'}},
                {'label': '📞 Contact', 'action': 'view_service', 'payload': {'url': self.nety_urls['contact'], 'name': 'Contact'}},
                {'label': '📱 Smartphones', 'action': 'view_category', 'payload': {'url': self.nety_urls['smartphones'], 'name': 'Smartphones'}}
            ]
        
        else:
            quick_replies = [
                {'label': '📱 Smartphones', 'action': 'view_category', 'payload': {'url': self.nety_urls['smartphones'], 'name': 'Smartphones'}},
                {'label': '🎧 Accessoires', 'action': 'view_category', 'payload': {'url': self.nety_urls['accessoires'], 'name': 'Accessoires'}},
                {'label': '📦 Paiement', 'action': 'view_service', 'payload': {'url': self.nety_urls['paiement'], 'name': 'Paiement'}},
                {'label': '💬 Contact', 'action': 'view_service', 'payload': {'url': self.nety_urls['contact'], 'name': 'Contact'}}
            ]
        
        return quick_replies
    
    def _format_product_response_with_tickets(self, products: List[Dict], search_term: str) -> Dict:
        """Formater la réponse avec les produits et les tickets"""
        if not products:
            return {
                'response': f"🔍 Désolé, je n'ai pas trouvé de produits pour '{search_term}' sur Nety.tn.\n\n💡 Essaie avec un autre mot-clé ou visite: https://www.nety.tn/fr/",
                'quick_replies': [
                    {'label': '📱 Smartphones', 'action': 'view_category', 'payload': {'url': self.nety_urls['smartphones'], 'name': 'Smartphones'}},
                    {'label': '🎧 Accessoires', 'action': 'view_category', 'payload': {'url': self.nety_urls['accessoires'], 'name': 'Accessoires'}},
                    {'label': '🔍 Nouvelle recherche', 'action': 'search', 'payload': {}}
                ]
            }
        
        response = f"🔍 **Résultats pour '{search_term}' sur Nety.tn:**\n\n"
        
        for i, product in enumerate(products[:3], 1):
            response += f"**{i}. {product.get('name', 'Produit')}**\n"
            response += f"💰 {product.get('price', 'Voir site')}\n"
            if product.get('link'):
                response += f"🔗 [Voir sur Nety]({product.get('link')})\n"
            response += "\n"
        
        response += "---\n"
        response += "💬 **Tu veux plus d'infos sur un produit?**"
        
        quick_replies = self._get_quick_replies('product_query', products)
        
        return {
            'response': response,
            'quick_replies': quick_replies
        }
    
    def _is_product_query(self, message: str) -> bool:
        """Detect if message is asking for products"""
        message_lower = message.lower()
        
        fr_keywords = ['cherche', 'trouve', 'produit', 'article', 'acheter', 
                      'prix', 'combien', 'disponible', 'en stock', 'site',
                      'nety', 'ordinateur', 'pc', 'phone', 'téléphone',
                      'tv', 'télé', 'réfrigérateur', 'machine', 'lave',
                      'smartphone', 'accessoire']
        
        ar_keywords = ['شنو', 'شكون', 'كيفاش', 'المنتج', 'سعر', 'شراء',
                      'نتي', 'كمبيوتر', 'موبايل', 'تلفاز', 'غسالة',
                      'شنو', 'عندك', 'شكون']
        
        en_keywords = ['product', 'price', 'buy', 'shop', 'search', 'find',
                      'laptop', 'phone', 'computer', 'tv', 'fridge']
        
        all_keywords = fr_keywords + ar_keywords + en_keywords
        return any(keyword in message_lower for keyword in all_keywords)
    
    def _extract_search_term(self, message: str) -> str:
        """Extract search term from message"""
        phrases_to_remove = [
            'cherche', 'trouve', 'produit', 'article', 'acheter',
            'prix', 'combien', 'disponible', 'en stock', 'site nety',
            'شنو', 'شكون', 'كيفاش', 'المنتج', 'سعر', 'شراء',
            'product', 'price', 'buy', 'shop', 'search', 'find',
            'nety', 'tn', 'www', 'com', 'a3tini', 'les', 'elmawjodin',
            'عندك', 'شكون', 'شنو'
        ]
        
        clean_message = message.lower()
        for phrase in phrases_to_remove:
            clean_message = clean_message.replace(phrase, '')
        
        clean_message = re.sub(r'[^\w\s]', '', clean_message)
        clean_message = re.sub(r'\s+', ' ', clean_message).strip()
        
        if len(clean_message) < 2:
            return message.strip()
        
        words = clean_message.split()
        if len(words) > 5:
            return ' '.join(words[:5])
        
        return clean_message
    
    # ============ MAIN SEND MESSAGE ============
    
    def send_message(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Send a message with Nety.tn scraping and quick replies"""
        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
            
            is_product = self._is_product_query(message)
            search_term = None
            
            if is_product:
                search_term = self._extract_search_term(message)
                print(f"🔍 Product query detected: '{search_term}'")
            
            gemini_result = self._get_gemini_response(message, context)
            intent = gemini_result.get('intent', 'general_query')
            quick_replies = []
            
            if is_product and search_term and len(search_term) > 1:
                products = self._search_nety_products(search_term, limit=5)
                
                if products:
                    formatted = self._format_product_response_with_tickets(products, search_term)
                    final_response = formatted['response']
                    quick_replies = formatted.get('quick_replies', [])
                    intent = 'product_query'
                else:
                    final_response = f"🔍 Je n'ai pas trouvé '{search_term}' sur Nety.tn.\n\n💡 Essaie avec d'autres mots-clés ou visite: https://www.nety.tn/fr/"
                    quick_replies = [
                        {'label': '📱 Smartphones', 'action': 'view_category', 'payload': {'url': self.nety_urls['smartphones'], 'name': 'Smartphones'}},
                        {'label': '🎧 Accessoires', 'action': 'view_category', 'payload': {'url': self.nety_urls['accessoires'], 'name': 'Accessoires'}},
                        {'label': '🔍 Nouvelle recherche', 'action': 'search', 'payload': {}}
                    ]
                    intent = 'product_not_found'
            else:
                final_response = gemini_result.get('response', self._get_fallback_response_short(message))
                quick_replies = self._get_quick_replies(intent)
            
            # Store in history
            self.conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': final_response,
                'timestamp': datetime.now().isoformat()
            })
            
            self.conversation_metadata['total_messages'] += 2
            self.conversation_metadata['user_messages'] += 1
            self.conversation_metadata['bot_messages'] += 1
            
            return {
                'success': True,
                'response': final_response,
                'model': self.model,
                'intent': intent,
                'confidence': 0.85,
                'history_count': len(self.conversation_history),
                'quick_replies': quick_replies
            }
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return {
                'success': False,
                'response': self._get_fallback_response_short(message),
                'intent': 'error',
                'quick_replies': [
                    {'label': '📱 Smartphones', 'action': 'view_category', 'payload': {'url': self.nety_urls['smartphones'], 'name': 'Smartphones'}},
                    {'label': '💬 Contact', 'action': 'view_service', 'payload': {'url': self.nety_urls['contact'], 'name': 'Contact'}}
                ]
            }
    
    def _get_gemini_response(self, message: str, context: Dict = None) -> Dict:
        """Get response from Gemini API"""
        try:
            messages = []
            
            system_prompt = """أنت مساعد متجر Nety.tn. 
            
            قواعد الرد:
            1. **الردود قصيرة ومباشرة** (ماكس 3-4 جمل)
            2. استخدم **1, 2, 3** للتنظيم
            3. لا تقدم معلومات زائدة
            4. اسأل سؤال واحد فقط في النهاية
            
            إذا سأل المستخدم عن منتج، ابحث له في موقع Nety.tn.
            إذا سأل عن خدمات، وجهه للروابط المناسبة."""
            
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
            for msg in self.conversation_history[-10:]:
                messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })
            
            full_message = message
            if context:
                full_message = f"Context: {json.dumps(context, ensure_ascii=False)}\nUser: {message}"
            
            messages.append({
                "role": "user",
                "content": full_message
            })
            
            url = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 150,
                "top_p": 0.9
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": os.environ.get('SITE_URL', 'http://localhost:5000'),
                "X-Title": "E-Commerce Chatbot"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    bot_response = result['choices'][0]['message']['content']
                    intent = self._extract_intent(bot_response)
                    return {
                        'success': True,
                        'response': self._format_response_short(bot_response, message),
                        'intent': intent
                    }
            
            return {
                'success': False,
                'response': self._get_fallback_response_short(message),
                'intent': 'fallback'
            }
            
        except Exception as e:
            print(f"⚠️ Gemini error: {e}")
            return {
                'success': False,
                'response': self._get_fallback_response_short(message),
                'intent': 'fallback'
            }
    
    # ============ FORMATTING METHODS ============
    
    def _format_response_short(self, response: str, user_message: str = None) -> str:
        """Format response to be SHORT and STRUCTURED"""
        if len(response.split()) < 30:
            return response
        
        lines = response.strip().split('\n')
        points = []
        
        for line in lines:
            line = line.strip()
            if any(line.startswith(str(i) + '.') or line.startswith(str(i) + '-') for i in range(1, 10)):
                for i in range(1, 10):
                    if line.startswith(str(i) + '.') or line.startswith(str(i) + '-'):
                        clean = line.replace(str(i) + '.', '').replace(str(i) + '-', '').strip()
                        points.append(f"{i}. {clean}")
                        break
            elif '•' in line or '*' in line:
                clean = line.replace('•', '').replace('*', '').strip()
                if clean and len(clean) < 50:
                    points.append(f"• {clean}")
        
        result = []
        if points:
            result.append('\n'.join(points[:3]))
        else:
            sentences = [s.strip() for s in response.split('.') if len(s.strip()) > 10]
            if sentences:
                result.append('. '.join(sentences[:2]) + '.')
            else:
                result.append(response[:100])
        
        closings = [
            "\nشنو تحب تسأل؟",
            "\nشنو تحب بالضبط؟",
            "\nشنو تحب تعرف؟"
        ]
        result.append(random.choice(closings))
        
        final_response = '\n'.join(result)
        if len(final_response) > 200:
            final_response = final_response[:200] + "..."
        
        return final_response
    
    def _get_fallback_response_short(self, message: str) -> str:
        """Short fallback responses"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['مرحب', 'اهلا', 'سلام', 'bonjour', 'hello']):
            return """مرحباً! أنا هنا لمساعدتك.

شنو تحب؟ 📱🎧💳"""
        
        elif any(word in message_lower for word in ['منتج', 'شراء', 'prix', 'product']):
            return """🔍 Je peux chercher sur Nety.tn!

Donne-moi le nom du produit que tu cherches."""
        
        elif any(word in message_lower for word in ['طلب', 'tracer', 'order']):
            return """📦 Pour suivre ta commande:

Donne-moi le numéro de commande."""
        
        else:
            return """أنا هنا لمساعدتك.

شنو تحتاج؟ 📱🎧💳"""
    
    def _extract_intent(self, response: str) -> str:
        """Extract intent from response"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['منتج', 'شراء', 'prix', 'product']):
            return 'product_query'
        elif any(word in response_lower for word in ['طلب', 'tracer', 'order']):
            return 'order_query'
        elif any(word in response_lower for word in ['ارجاع', 'retour']):
            return 'return_query'
        else:
            return 'general_query'
    
    # ============ UTILITY METHODS ============
    
    def get_conversation_history(self, limit: int = None) -> List[Dict]:
        """Get conversation history with optional limit"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of conversation"""
        return {
            'total_messages': len(self.conversation_history),
            'user_messages': self.conversation_metadata['user_messages'],
            'bot_messages': self.conversation_metadata['bot_messages'],
            'started_at': self.conversation_metadata['started_at'],
            'last_message': self.conversation_history[-1] if self.conversation_history else None
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.conversation_metadata = {
            'started_at': datetime.now().isoformat(),
            'total_messages': 0,
            'user_messages': 0,
            'bot_messages': 0
        }
        if hasattr(self, 'nety_scraper'):
            self.nety_scraper.clear_cache()
        print("🗑️ تم مسح تاريخ المحادثة والكاش")
    
    def switch_model(self, new_model: str) -> bool:
        """Switch to a different model"""
        try:
            if new_model in self.available_models:
                self.model = new_model
                print(f"✅ Switched to model: {new_model}")
                return True
            else:
                print(f"⚠️ Model '{new_model}' not in available list. Trying anyway...")
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

    def _try_fallback_model(self, message: str) -> Dict[str, Any]:
        """Try fallback models if primary fails"""
        fallback_models = [
            "google/gemma-4-26b-a4b-it:free",
            "openrouter/free",
            "qwen/qwen3-coder:free"
        ]
        
        original_model = self.model
        
        for fallback in fallback_models:
            if fallback != original_model:
                print(f"🔄 Trying fallback model: {fallback}")
                self.model = fallback
                result = self.send_message(message)
                self.model = original_model
                
                if result.get('success'):
                    return result
        
        self.model = original_model
        return {
            'success': False,
            'response': self._get_fallback_response_short(message),
            'intent': 'fallback'
        }