import os
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
from urllib.parse import urljoin, quote
import re

class NetyScraper:
    """Service de scraping pour Nety.tn"""
    
    def __init__(self):
        self.base_url = "https://www.nety.tn/fr/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Cache pour éviter de scraper plusieurs fois les mêmes pages
        self.cache = {}
        
        # URLs des catégories
        self.categories = {
            'smartphones': '8-smartphones',
            'accessoires': '9-accessoires',
            'tablettes': '10-tablettes',
            'ordinateurs': '11-ordinateurs',
            'tv': '12-tv'
        }
    
    def search_products(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Rechercher des produits sur Nety.tn en parcourant les catégories
        
        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats
        
        Returns:
            Liste de produits avec nom, prix, image, lien
        """
        try:
            # Vérifier le cache
            cache_key = f"search_{query}_{limit}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            print(f"🔍 Recherche de: {query} sur Nety.tn")
            
            products = []
            query_lower = query.lower()
            
            # Parcourir toutes les catégories
            for category_name, category_url in self.categories.items():
                try:
                    category_products = self._scrape_category(category_url, limit)
                    
                    # Filtrer les produits qui correspondent à la recherche
                    for product in category_products:
                        product_name = product.get('name', '').lower()
                        if query_lower in product_name or any(word in product_name for word in query_lower.split()):
                            if len(products) < limit:
                                products.append(product)
                    
                    if len(products) >= limit:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Erreur scraping catégorie {category_name}: {e}")
                    continue
            
            # Si aucun produit trouvé, chercher dans toutes les catégories
            if not products:
                products = self._search_all_categories(query, limit)
            
            # Mettre en cache
            self.cache[cache_key] = products
            
            print(f"✅ Trouvé {len(products)} produits pour '{query}'")
            return products
            
        except Exception as e:
            print(f"❌ Erreur scraping: {e}")
            return []
    
    def _scrape_category(self, category_url: str, limit: int = 10) -> List[Dict]:
        """Scraper une catégorie spécifique"""
        try:
            url = urljoin(self.base_url, category_url)
            
            # Vérifier le cache
            cache_key = f"category_{category_url}"
            if cache_key in self.cache:
                return self.cache[cache_key][:limit]
            
            print(f"📂 Scraping catégorie: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Chercher les produits dans la catégorie
            product_items = soup.find_all('article', class_='product-miniature')
            
            if not product_items:
                product_items = soup.find_all('div', class_='product-item')
            
            if not product_items:
                product_items = soup.find_all('div', class_='product-container')
            
            for item in product_items[:limit]:
                try:
                    product_data = self._extract_product_from_item(item)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    print(f"⚠️ Erreur extraction produit: {e}")
                    continue
            
            # Mettre en cache
            self.cache[cache_key] = products
            
            return products
            
        except Exception as e:
            print(f"❌ Erreur scraping catégorie: {e}")
            return []
    
    def _extract_product_from_item(self, item) -> Optional[Dict]:
        """Extraire les données d'un élément produit"""
        try:
            # Nom du produit
            name_elem = item.find('h2', class_='product-title') or item.find('div', class_='product-name')
            if not name_elem:
                name_elem = item.find('a', class_='product-name')
            if not name_elem:
                name_elem = item.find('h3')
            if not name_elem:
                name_elem = item.find('a', class_='product-thumbnail')
            
            name = name_elem.text.strip() if name_elem else "Nom inconnu"
            
            # Lien du produit
            link_elem = item.find('a', href=True)
            link = link_elem['href'] if link_elem else ""
            if link and not link.startswith('http'):
                link = urljoin(self.base_url, link)
            
            # Prix
            price_elem = item.find('span', class_='price') or item.find('div', class_='product-price')
            if not price_elem:
                price_elem = item.find('span', class_='product-price')
            if not price_elem:
                price_elem = item.find('span', class_='price')
            
            price = price_elem.text.strip() if price_elem else "Prix non disponible"
            
            # Image
            img_elem = item.find('img')
            image = img_elem.get('src', '') if img_elem else ""
            if image and not image.startswith('http'):
                image = urljoin(self.base_url, image)
            
            # Description courte
            desc_elem = item.find('div', class_='product-description')
            description = desc_elem.text.strip()[:150] + "..." if desc_elem else ""
            
            return {
                'name': self._clean_text(name),
                'price': self._clean_text(price),
                'link': link,
                'image': image,
                'description': self._clean_text(description)
            }
        except Exception as e:
            print(f"⚠️ Erreur extraction: {e}")
            return None
    
    def _search_all_categories(self, query: str, limit: int) -> List[Dict]:
        """Rechercher dans toutes les catégories"""
        all_products = []
        
        for category_name, category_url in self.categories.items():
            try:
                products = self._scrape_category(category_url, limit)
                all_products.extend(products)
            except:
                continue
        
        # Filtrer par mots-clés
        query_words = query.lower().split()
        filtered = []
        
        for product in all_products:
            product_name = product.get('name', '').lower()
            if any(word in product_name for word in query_words):
                filtered.append(product)
                if len(filtered) >= limit:
                    break
        
        return filtered
    
    def _clean_text(self, text: str) -> str:
        """Nettoyer le texte"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-\.\,\€\d]', '', text)
        return text.strip()
    
    def get_product_details(self, url: str) -> Optional[Dict]:
        """Obtenir les détails d'un produit spécifique"""
        try:
            cache_key = f"product_{url}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product = {
                'url': url,
                'name': '',
                'price': '',
                'description': '',
                'images': [],
                'specifications': {},
                'availability': ''
            }
            
            # Nom
            name_elem = soup.find('h1', class_='product-title') or soup.find('h1')
            if name_elem:
                product['name'] = name_elem.text.strip()
            
            # Prix
            price_elem = soup.find('span', class_='price') or soup.find('div', class_='product-price')
            if price_elem:
                product['price'] = price_elem.text.strip()
            
            # Description
            desc_elem = soup.find('div', class_='product-description') or soup.find('div', class_='description')
            if desc_elem:
                product['description'] = desc_elem.text.strip()
            
            # Images
            images = soup.find_all('img', class_='product-image')
            for img in images:
                src = img.get('src', '')
                if src:
                    product['images'].append(urljoin(self.base_url, src))
            
            # Caractéristiques
            spec_sections = soup.find_all('div', class_='product-features')
            for section in spec_sections:
                rows = section.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()
                        product['specifications'][key] = value
            
            # Disponibilité
            avail_elem = soup.find('span', class_='product-availability')
            if avail_elem:
                product['availability'] = avail_elem.text.strip()
            
            self.cache[cache_key] = product
            return product
            
        except Exception as e:
            print(f"❌ Erreur scraping produit: {e}")
            return None
    
    def clear_cache(self):
        """Vider le cache"""
        self.cache = {}
        print("🗑️ Cache vidé")

# Instance singleton
scraper = NetyScraper()