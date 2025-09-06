#!/usr/bin/env python3
"""
Polygon.io MCP Utility Module
Handles all Polygon.io API interactions and data processing
"""

import os
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PolygonAPI:
    """Enhanced Polygon.io API wrapper with better error handling"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PolygonMCP/1.0'
        })
    
    def get_ticker_details(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive ticker details"""
        url = f"{self.base_url}/v3/reference/tickers/{ticker}"
        params = {"apikey": self.api_key}
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_previous_close(self, ticker: str) -> Dict[str, Any]:
        """Get previous close data for a ticker"""
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/prev"
        params = {"apikey": self.api_key}
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_aggregates(self, ticker: str, multiplier: int = 1, timespan: str = "day", 
                      from_date: str = None, to_date: str = None) -> Dict[str, Any]:
        """Get aggregate bars for a ticker"""
        if not from_date:
            # Default to last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            from_date = start_date.strftime("%Y-%m-%d")
            to_date = end_date.strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        params = {"apikey": self.api_key}
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_news(self, ticker: str = None, limit: int = 10) -> Dict[str, Any]:
        """Get news articles"""
        url = f"{self.base_url}/v2/reference/news"
        params = {"apikey": self.api_key, "limit": limit}
        if ticker:
            params["ticker"] = ticker
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        url = f"{self.base_url}/v1/marketstatus/now"
        params = {"apikey": self.api_key}
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

def extract_ticker(query: str) -> Optional[str]:
    """Extract ticker symbol from natural language query"""
    # Common ticker patterns
    ticker_patterns = [
        r'\b([A-Z]{1,5})\b(?:\s+(?:stock|price|shares|ticker))',  # AAPL stock
        r'(?:ticker|symbol)\s+([A-Z]{1,5})\b',  # ticker AAPL
        r'\$([A-Z]{1,5})\b',  # $AAPL
        r'\b([A-Z]{2,5})\b',  # Standalone tickers (2-5 chars)
    ]
    
    # Known company name to ticker mappings
    company_mappings = {
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'amazon': 'AMZN',
        'tesla': 'TSLA',
        'meta': 'META',
        'facebook': 'META',
        'nvidia': 'NVDA',
        'netflix': 'NFLX',
        'disney': 'DIS',
        'walmart': 'WMT',
        'coca cola': 'KO',
        'pepsi': 'PEP',
        'johnson': 'JNJ',
        'visa': 'V',
        'mastercard': 'MA',
        'intel': 'INTC',
        'amd': 'AMD',
        'ibm': 'IBM',
        'oracle': 'ORCL',
        'salesforce': 'CRM',
        'adobe': 'ADBE',
        'zoom': 'ZM',
        'uber': 'UBER',
        'lyft': 'LYFT',
        'airbnb': 'ABNB',
        'spotify': 'SPOT',
        'twitter': 'TWTR',
        'snapchat': 'SNAP',
        'pinterest': 'PINS',
        'square': 'SQ',
        'paypal': 'PYPL',
        'coinbase': 'COIN',
        'robinhood': 'HOOD'
    }
    
    query_lower = query.lower()
    
    # Check for company names first
    for company, ticker in company_mappings.items():
        if company in query_lower:
            return ticker
    
    # Then check for ticker patterns
    for pattern in ticker_patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        if matches:
            ticker = matches[0].upper()
            # Validate ticker length
            if 1 <= len(ticker) <= 5:
                return ticker
    
    return None

def format_price(price: Any) -> str:
    """Format price with proper currency formatting"""
    try:
        if price is None or price == 'N/A':
            return 'N/A'
        return f"${float(price):,.2f}"
    except (ValueError, TypeError):
        return str(price)

def format_volume(volume: Any) -> str:
    """Format volume with proper number formatting"""
    try:
        if volume is None or volume == 'N/A':
            return 'N/A'
        vol = int(volume)
        if vol >= 1_000_000:
            return f"{vol/1_000_000:.1f}M"
        elif vol >= 1_000:
            return f"{vol/1_000:.1f}K"
        else:
            return f"{vol:,}"
    except (ValueError, TypeError):
        return str(volume)

def analyze_stock_query(query: str, polygon_api: PolygonAPI) -> str:
    """Analyze a stock query and return comprehensive information"""
    ticker = extract_ticker(query)
    
    if not ticker:
        return "❌ Please specify a stock ticker (e.g., AAPL, MSFT, GOOGL) in your query."
    
    response = f"## 📊 Analysis for {ticker}\n\n"
    
    # Get ticker details
    details = polygon_api.get_ticker_details(ticker)
    if details.get('results'):
        result = details['results']
        response += f"**Company:** {result.get('name', 'N/A')}\n"
        response += f"**Market:** {result.get('market', 'N/A').upper()}\n"
        response += f"**Type:** {result.get('type', 'N/A')}\n"
        response += f"**Currency:** {result.get('currency_name', 'USD').upper()}\n"
        
        # Market cap if available
        if result.get('market_cap'):
            market_cap = result['market_cap']
            if market_cap >= 1_000_000_000:
                response += f"**Market Cap:** ${market_cap/1_000_000_000:.1f}B\n"
            elif market_cap >= 1_000_000:
                response += f"**Market Cap:** ${market_cap/1_000_000:.1f}M\n"
            else:
                response += f"**Market Cap:** ${market_cap:,.0f}\n"
        
        response += "\n"
    elif details.get('error'):
        response += f"⚠️ Could not fetch ticker details: {details['error']}\n\n"
    
    # Get previous close data
    prev_close = polygon_api.get_previous_close(ticker)
    if prev_close.get('results') and len(prev_close['results']) > 0:
        result = prev_close['results'][0]
        close_price = result.get('c')
        high_price = result.get('h')
        low_price = result.get('l')
        open_price = result.get('o')
        volume = result.get('v')
        
        response += f"**📈 Previous Close Data:**\n"
        response += f"- **Close:** {format_price(close_price)}\n"
        response += f"- **Open:** {format_price(open_price)}\n"
        response += f"- **High:** {format_price(high_price)}\n"
        response += f"- **Low:** {format_price(low_price)}\n"
        response += f"- **Volume:** {format_volume(volume)} shares\n\n"
        
        # Calculate daily change if we have open and close
        if open_price and close_price:
            try:
                change = float(close_price) - float(open_price)
                change_pct = (change / float(open_price)) * 100
                change_emoji = "📈" if change >= 0 else "📉"
                response += f"**Daily Change:** {change_emoji} {change:+.2f} ({change_pct:+.2f}%)\n\n"
            except (ValueError, TypeError):
                pass
    elif prev_close.get('error'):
        response += f"⚠️ Could not fetch price data: {prev_close['error']}\n\n"
    
    # Get recent news
    news = polygon_api.get_news(ticker, limit=3)
    if news.get('results'):
        response += "**📰 Recent News:**\n"
        for article in news['results'][:3]:
            title = article.get('title', 'No title')
            published = article.get('published_utc', 'Unknown date')
            url = article.get('article_url', '#')
            # Format date
            try:
                if published != 'Unknown date':
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    formatted_date = pub_date.strftime('%Y-%m-%d %H:%M')
                else:
                    formatted_date = published
            except:
                formatted_date = published
            
            response += f"- [{title}]({url}) - {formatted_date}\n"
        response += "\n"
    elif news.get('error'):
        response += f"⚠️ Could not fetch news: {news['error']}\n\n"
    
    # Add disclaimer
    response += "---\n"
    response += "*Not financial advice. For informational purposes only.*"
    
    return response

def save_analysis_report(content: str, ticker: str) -> str:
    """Save analysis report to file"""
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/{ticker}_analysis_{timestamp}.md"
    
    with open(filename, 'w') as f:
        f.write(f"# {ticker} Stock Analysis Report\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(content)
    
    return filename

def test_polygon_api():
    """Test function for Polygon API"""
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("❌ POLYGON_API_KEY not found in environment variables")
        return False
    
    print(f"✅ Testing Polygon API with key: {api_key[:10]}...")
    
    polygon_api = PolygonAPI(api_key)
    
    # Test ticker details
    print("\n🧪 Testing ticker details for AAPL...")
    details = polygon_api.get_ticker_details("AAPL")
    if details.get('results'):
        print(f"✅ Company: {details['results'].get('name')}")
    else:
        print(f"❌ Error: {details.get('error')}")
    
    # Test previous close
    print("\n🧪 Testing previous close for AAPL...")
    prev_close = polygon_api.get_previous_close("AAPL")
    if prev_close.get('results'):
        print(f"✅ Close price: ${prev_close['results'][0].get('c')}")
    else:
        print(f"❌ Error: {prev_close.get('error')}")
    
    # Test news
    print("\n🧪 Testing news for AAPL...")
    news = polygon_api.get_news("AAPL", limit=2)
    if news.get('results'):
        print(f"✅ Found {len(news['results'])} news articles")
    else:
        print(f"❌ Error: {news.get('error')}")
    
    # Test query analysis
    print("\n🧪 Testing query analysis...")
    analysis = analyze_stock_query("What is the current price of Apple?", polygon_api)
    print(f"✅ Analysis generated ({len(analysis)} characters)")
    
    return True

if __name__ == "__main__":
    test_polygon_api()

