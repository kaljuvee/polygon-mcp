#!/usr/bin/env python3
"""
Simple query tests that demonstrate the basic functionality
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def test_simple_queries():
    """Test simple queries like those in the blog post"""
    
    # Import our simple demo functions
    try:
        from simple_demo import PolygonAPI, extract_ticker, analyze_query
    except ImportError:
        print("❌ Could not import simple_demo module")
        return False
    
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("❌ POLYGON_API_KEY not found")
        return False
    
    polygon_api = PolygonAPI(api_key)
    
    # Test queries from the blog post
    test_queries = [
        "Get the latest price of Microsoft",
        "Show me AAPL information", 
        "What's the latest on TSLA?",
        "NVDA stock details",
        "META news"
    ]
    
    print("🧪 Testing Simple Queries")
    print("=" * 50)
    
    results = {}
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 30)
        
        # Extract ticker
        ticker = extract_ticker(query)
        print(f"Extracted ticker: {ticker}")
        
        if ticker:
            # Run analysis
            try:
                result = analyze_query(query, polygon_api)
                print(f"Analysis length: {len(result)} characters")
                print(f"First 200 chars: {result[:200]}...")
                
                results[f"query_{i}"] = {
                    "query": query,
                    "ticker": ticker,
                    "result": result,
                    "success": True
                }
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                results[f"query_{i}"] = {
                    "query": query,
                    "ticker": ticker,
                    "error": str(e),
                    "success": False
                }
        else:
            print("⚠️ No ticker extracted")
            results[f"query_{i}"] = {
                "query": query,
                "ticker": None,
                "error": "No ticker extracted",
                "success": False
            }
    
    # Save results
    with open("test-data/simple_queries_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Simple query tests completed")
    print(f"📁 Results saved to test-data/simple_queries_results.json")
    
    # Summary
    successful = sum(1 for r in results.values() if r.get('success', False))
    total = len(results)
    print(f"📊 Success rate: {successful}/{total} ({successful/total*100:.1f}%)")
    
    return successful == total

if __name__ == "__main__":
    success = test_simple_queries()
    sys.exit(0 if success else 1)

