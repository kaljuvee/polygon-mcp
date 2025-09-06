import streamlit as st
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Stock Market Analysis Demo",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

class PolygonAPI:
    """Simple Polygon.io API wrapper"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
    
    def get_ticker_details(self, ticker: str) -> Dict[str, Any]:
        """Get ticker details"""
        url = f"{self.base_url}/v3/reference/tickers/{ticker}"
        params = {"apikey": self.api_key}
        try:
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_latest_quote(self, ticker: str) -> Dict[str, Any]:
        """Get latest quote for a ticker"""
        url = f"{self.base_url}/v2/last/trade/{ticker}"
        params = {"apikey": self.api_key}
        try:
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_aggregates(self, ticker: str, multiplier: int = 1, timespan: str = "day", 
                      from_date: str = "2023-01-01", to_date: str = "2024-01-01") -> Dict[str, Any]:
        """Get aggregate bars for a ticker"""
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        params = {"apikey": self.api_key}
        try:
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_news(self, ticker: str = None, limit: int = 10) -> Dict[str, Any]:
        """Get news articles"""
        url = f"{self.base_url}/v2/reference/news"
        params = {"apikey": self.api_key, "limit": limit}
        if ticker:
            params["ticker"] = ticker
        try:
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

def extract_ticker(query: str) -> str:
    """Simple ticker extraction from query"""
    import re
    # Look for common ticker patterns (2-5 uppercase letters)
    ticker_pattern = r'\b[A-Z]{2,5}\b'
    matches = re.findall(ticker_pattern, query.upper())
    
    # Common company name to ticker mapping
    company_tickers = {
        'MICROSOFT': 'MSFT',
        'APPLE': 'AAPL',
        'GOOGLE': 'GOOGL',
        'AMAZON': 'AMZN',
        'TESLA': 'TSLA',
        'META': 'META',
        'NVIDIA': 'NVDA'
    }
    
    for company, ticker in company_tickers.items():
        if company in query.upper():
            return ticker
    
    return matches[0] if matches else None

def analyze_query(query: str, polygon_api: PolygonAPI) -> str:
    """Simple analysis function using Polygon data"""
    ticker = extract_ticker(query)
    
    if not ticker:
        return "❌ Please specify a stock ticker (e.g., AAPL, MSFT, GOOGL) in your query."
    
    response = f"## Analysis for {ticker}\n\n"
    
    # Get ticker details
    details = polygon_api.get_ticker_details(ticker)
    if details.get('results'):
        result = details['results']
        response += f"**Company:** {result.get('name', 'N/A')}\n"
        response += f"**Market:** {result.get('market', 'N/A')}\n"
        response += f"**Type:** {result.get('type', 'N/A')}\n"
        response += f"**Currency:** {result.get('currency_name', 'N/A')}\n\n"
    elif details.get('error'):
        response += f"⚠️ Could not fetch ticker details: {details['error']}\n\n"
    
    # Get latest quote
    quote = polygon_api.get_latest_quote(ticker)
    if quote.get('results'):
        result = quote['results']
        price = result.get('p', 'N/A')
        size = result.get('s', 'N/A')
        timestamp = result.get('t', 'N/A')
        response += f"**Latest Trade:**\n"
        response += f"- Price: ${price}\n"
        response += f"- Size: {size} shares\n"
        response += f"- Timestamp: {timestamp}\n\n"
    elif quote.get('error'):
        response += f"⚠️ Could not fetch latest quote: {quote['error']}\n\n"
    
    # Get recent news
    news = polygon_api.get_news(ticker, limit=3)
    if news.get('results'):
        response += "**Recent News:**\n"
        for article in news['results'][:3]:
            title = article.get('title', 'No title')
            published = article.get('published_utc', 'Unknown date')
            url = article.get('article_url', '#')
            response += f"- [{title}]({url}) - {published}\n"
        response += "\n"
    elif news.get('error'):
        response += f"⚠️ Could not fetch news: {news['error']}\n\n"
    
    response += "---\n*Not financial advice. For informational purposes only.*"
    
    return response

def save_analysis_report(content: str, ticker: str) -> str:
    """Save analysis report to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{ticker}_{timestamp}.md"
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    filepath = os.path.join("reports", filename)
    with open(filepath, "w") as f:
        f.write(content)
    
    return filepath

# Initialize API
@st.cache_resource
def initialize_polygon_api():
    return PolygonAPI(os.getenv("POLYGON_API_KEY"))

# Main app
def main():
    st.title("📈 Stock Market Analysis Demo")
    st.markdown("*Simplified demo using Polygon.io data*")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This is a simplified demo that showcases:
        - Real-time stock data via Polygon.io
        - Ticker information and latest quotes
        - Recent news for stocks
        - Report generation
        """)
        
        st.header("Example Queries")
        st.markdown("""
        - "Get the latest price of Microsoft"
        - "Show me AAPL information"
        - "What's the latest on TSLA?"
        - "NVDA stock details"
        """)
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize API
    polygon_api = initialize_polygon_api()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about stocks (e.g., 'AAPL price', 'Microsoft info')..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Fetching data..."):
                try:
                    response = analyze_query(prompt, polygon_api)
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Offer to save report
                    ticker = extract_ticker(prompt)
                    if ticker and st.button(f"💾 Save {ticker} Report"):
                        filepath = save_analysis_report(response, ticker)
                        st.success(f"Report saved to: {filepath}")
                
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()

