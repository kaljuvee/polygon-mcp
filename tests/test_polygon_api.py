#!/usr/bin/env python3
"""
Command line tests for Polygon.io API functionality
Replicates queries from the blog post
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PolygonAPI:
    """Simple Polygon.io API wrapper for testing"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
    
    def get_ticker_details(self, ticker: str):
        """Get ticker details"""
        url = f"{self.base_url}/v3/reference/tickers/{ticker}"
        params = {"apikey": self.api_key}
        try:
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_latest_quote(self, ticker: str):
        """Get latest quote for a ticker"""
        url = f"{self.base_url}/v2/last/trade/{ticker}"
        params = {"apikey": self.api_key}
        try:
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_aggregates(self, ticker: str, multiplier: int = 1, timespan: str = "day", 
                      from_date: str = "2023-01-01", to_date: str = "2024-01-01"):
        """Get aggregate bars for a ticker"""
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        params = {"apikey": self.api_key}
        try:
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_news(self, ticker: str = None, limit: int = 10):
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

def save_test_data(data, filename):
    """Save test data to JSON file"""
    filepath = f"test-data/{filename}"
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved test data to {filepath}")

def test_microsoft_price():
    """Test: Get the latest price of Microsoft"""
    print("\n🧪 Test 1: Get the latest price of Microsoft")
    print("-" * 50)
    
    api = PolygonAPI(os.getenv("POLYGON_API_KEY"))
    
    # Get ticker details
    details = api.get_ticker_details("MSFT")
    print(f"Ticker Details: {json.dumps(details, indent=2)}")
    save_test_data(details, "msft_details.json")
    
    # Get latest quote
    quote = api.get_latest_quote("MSFT")
    print(f"Latest Quote: {json.dumps(quote, indent=2)}")
    save_test_data(quote, "msft_quote.json")
    
    return details, quote

def test_apple_deep_dive():
    """Test: Do a deep dive on AAPL over the last year"""
    print("\n🧪 Test 2: Deep dive on AAPL over the last year")
    print("-" * 50)
    
    api = PolygonAPI(os.getenv("POLYGON_API_KEY"))
    
    # Calculate date range (last year)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    from_date = start_date.strftime("%Y-%m-%d")
    to_date = end_date.strftime("%Y-%m-%d")
    
    # Get ticker details
    details = api.get_ticker_details("AAPL")
    print(f"AAPL Details: {json.dumps(details, indent=2)}")
    save_test_data(details, "aapl_details.json")
    
    # Get aggregates (daily data for last year)
    aggregates = api.get_aggregates("AAPL", 1, "day", from_date, to_date)
    print(f"AAPL Aggregates (last year): {len(aggregates.get('results', []))} data points")
    save_test_data(aggregates, "aapl_aggregates.json")
    
    # Get recent news
    news = api.get_news("AAPL", limit=5)
    print(f"AAPL News: {len(news.get('results', []))} articles")
    save_test_data(news, "aapl_news.json")
    
    return details, aggregates, news

def test_tesla_nvidia_comparison():
    """Test: Compare TSLA and NVDA performance"""
    print("\n🧪 Test 3: Compare TSLA and NVDA performance")
    print("-" * 50)
    
    api = PolygonAPI(os.getenv("POLYGON_API_KEY"))
    
    # Calculate date range (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    from_date = start_date.strftime("%Y-%m-%d")
    to_date = end_date.strftime("%Y-%m-%d")
    
    comparison_data = {}
    
    for ticker in ["TSLA", "NVDA"]:
        print(f"\nAnalyzing {ticker}...")
        
        # Get ticker details
        details = api.get_ticker_details(ticker)
        
        # Get aggregates
        aggregates = api.get_aggregates(ticker, 1, "day", from_date, to_date)
        
        # Get latest quote
        quote = api.get_latest_quote(ticker)
        
        # Get news
        news = api.get_news(ticker, limit=3)
        
        comparison_data[ticker] = {
            "details": details,
            "aggregates": aggregates,
            "quote": quote,
            "news": news
        }
        
        print(f"{ticker} - Latest Price: ${quote.get('results', {}).get('p', 'N/A')}")
        print(f"{ticker} - Data Points: {len(aggregates.get('results', []))}")
        print(f"{ticker} - News Articles: {len(news.get('results', []))}")
    
    save_test_data(comparison_data, "tsla_nvda_comparison.json")
    return comparison_data

def test_meta_news():
    """Test: What's the latest news on META?"""
    print("\n🧪 Test 4: Latest news on META")
    print("-" * 50)
    
    api = PolygonAPI(os.getenv("POLYGON_API_KEY"))
    
    # Get ticker details
    details = api.get_ticker_details("META")
    print(f"META Details: {json.dumps(details, indent=2)}")
    save_test_data(details, "meta_details.json")
    
    # Get latest news
    news = api.get_news("META", limit=10)
    print(f"META News: {len(news.get('results', []))} articles")
    
    # Print news headlines
    if news.get('results'):
        print("\nLatest Headlines:")
        for i, article in enumerate(news['results'][:5], 1):
            title = article.get('title', 'No title')
            published = article.get('published_utc', 'Unknown date')
            print(f"{i}. {title} ({published})")
    
    save_test_data(news, "meta_news.json")
    return details, news

def main():
    """Run all tests"""
    print("🚀 Starting Polygon.io API Tests")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("❌ Error: POLYGON_API_KEY not found in environment variables")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Run tests based on blog post examples
        test_microsoft_price()
        test_apple_deep_dive()
        test_tesla_nvidia_comparison()
        test_meta_news()
        
        print("\n🎉 All tests completed successfully!")
        print("📁 Test data saved to test-data/ directory")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

