import streamlit as st
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
import requests
import json
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Stock Market Analysis Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "analysis_reports" not in st.session_state:
    st.session_state.analysis_reports = []

class FinanceOutput(BaseModel):
    """Structured result from the guardrail check."""
    is_about_finance: bool
    reasoning: str

class PolygonAPI:
    """Simple Polygon.io API wrapper"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
    
    def get_ticker_details(self, ticker: str) -> Dict[str, Any]:
        """Get ticker details"""
        url = f"{self.base_url}/v3/reference/tickers/{ticker}"
        params = {"apikey": self.api_key}
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else {}
    
    def get_latest_quote(self, ticker: str) -> Dict[str, Any]:
        """Get latest quote for a ticker"""
        url = f"{self.base_url}/v2/last/trade/{ticker}"
        params = {"apikey": self.api_key}
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else {}
    
    def get_aggregates(self, ticker: str, multiplier: int = 1, timespan: str = "day", 
                      from_date: str = "2023-01-01", to_date: str = "2024-01-01") -> Dict[str, Any]:
        """Get aggregate bars for a ticker"""
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        params = {"apikey": self.api_key}
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else {}
    
    def get_news(self, ticker: str = None, limit: int = 10) -> Dict[str, Any]:
        """Get news articles"""
        url = f"{self.base_url}/v2/reference/news"
        params = {"apikey": self.api_key, "limit": limit}
        if ticker:
            params["ticker"] = ticker
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else {}

class FinancialAnalysisAgent:
    """Financial Analysis Agent using OpenAI"""
    
    def __init__(self, openai_client: AsyncOpenAI, polygon_api: PolygonAPI):
        self.client = openai_client
        self.polygon = polygon_api
        self.system_prompt = """
        You are a Financial Analysis Agent. Your role is to:
        
        1. Verify that queries are finance-related
        2. Use Polygon.io data to provide accurate financial analysis
        3. Include appropriate disclaimers
        4. Offer to save reports when analysis is comprehensive
        
        RULES:
        - Double-check all calculations
        - Limit news to ≤3 articles per ticker in date range
        - If data is unavailable, explain gracefully - never fabricate
        - Always include disclaimer: "Not financial advice. For informational purposes only."
        
        Available tools:
        - Polygon.io market data (quotes, aggregates, news, ticker details)
        - Report generation capabilities
        """
    
    async def validate_finance_query(self, query: str) -> FinanceOutput:
        """Validate if query is finance-related using guardrail"""
        guardrail_prompt = """
        Classify if the user query is finance-related.
        Include: stocks, ETFs, crypto, forex, market news, fundamentals, 
        economic indicators, ROI calculations, corporate actions.
        Exclude: non-financial topics, general questions, personal advice.
        
        Respond with JSON format: {"is_about_finance": boolean, "reasoning": "explanation"}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": guardrail_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return FinanceOutput(**result)
        except Exception as e:
            return FinanceOutput(is_about_finance=False, reasoning=f"Error in validation: {str(e)}")
    
    async def analyze_query(self, query: str) -> str:
        """Main analysis function"""
        # First validate the query
        validation = await self.validate_finance_query(query)
        
        if not validation.is_about_finance:
            return f"❌ This query doesn't appear to be finance-related. {validation.reasoning}\n\nPlease ask questions about stocks, market data, financial analysis, or related topics."
        
        # Extract ticker if mentioned
        ticker = self._extract_ticker(query)
        
        # Gather relevant data
        context_data = ""
        if ticker:
            # Get ticker details
            details = self.polygon.get_ticker_details(ticker)
            if details.get('results'):
                context_data += f"Ticker Details for {ticker}:\n{json.dumps(details['results'], indent=2)}\n\n"
            
            # Get latest quote
            quote = self.polygon.get_latest_quote(ticker)
            if quote.get('results'):
                context_data += f"Latest Quote for {ticker}:\n{json.dumps(quote['results'], indent=2)}\n\n"
            
            # Get recent news
            news = self.polygon.get_news(ticker, limit=3)
            if news.get('results'):
                context_data += f"Recent News for {ticker}:\n{json.dumps(news['results'][:3], indent=2)}\n\n"
        
        # Generate analysis using GPT
        analysis_prompt = f"""
        {self.system_prompt}
        
        User Query: {query}
        
        Available Data:
        {context_data}
        
        Provide a comprehensive analysis based on the available data. If specific data is requested but not available, explain what data would be needed and suggest alternatives.
        
        Always end with the disclaimer: "Not financial advice. For informational purposes only."
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "system", "content": analysis_prompt}],
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error generating analysis: {str(e)}"
    
    def _extract_ticker(self, query: str) -> Optional[str]:
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

def save_analysis_report(content: str, filename: str = None) -> str:
    """Save analysis report to file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_report_{timestamp}.md"
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    filepath = os.path.join("reports", filename)
    with open(filepath, "w") as f:
        f.write(content)
    
    return filepath

# Initialize APIs
@st.cache_resource
def initialize_apis():
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    polygon_api = PolygonAPI(os.getenv("POLYGON_API_KEY"))
    return FinancialAnalysisAgent(openai_client, polygon_api)

# Main app
def main():
    st.title("📈 Stock Market Analysis Agent")
    st.markdown("*Powered by OpenAI GPT-4 and Polygon.io*")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This demo replicates the functionality from the Polygon.io blog post:
        **"Creating stock market reports using OpenAI's GPT-5 and Agent SDK"**
        
        **Features:**
        - Real-time stock data via Polygon.io
        - AI-powered financial analysis
        - Report generation
        - Finance query validation
        """)
        
        st.header("Example Queries")
        st.markdown("""
        - "Get the latest price of Microsoft"
        - "Do a deep dive on AAPL over the last year"
        - "Compare TSLA and NVDA performance"
        - "What's the latest news on META?"
        """)
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize agent
    agent = initialize_apis()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about stocks, market data, or financial analysis..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    # Run async function
                    response = asyncio.run(agent.analyze_query(prompt))
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Offer to save report if it's a comprehensive analysis
                    if len(response) > 500 and "deep dive" in prompt.lower():
                        if st.button("💾 Save Analysis Report"):
                            filepath = save_analysis_report(response)
                            st.success(f"Report saved to: {filepath}")
                            st.session_state.analysis_reports.append(filepath)
                
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Display saved reports
    if st.session_state.analysis_reports:
        st.sidebar.header("Saved Reports")
        for report in st.session_state.analysis_reports:
            st.sidebar.markdown(f"📄 {os.path.basename(report)}")

if __name__ == "__main__":
    main()

