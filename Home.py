#!/usr/bin/env python3
"""
Polygon.io AI Chat - Streamlit Demo
Replicates functionality from Polygon.io blog post with OpenAI integration
"""

import streamlit as st
import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Dict, Any

# Import our utility module
from utils.polygon_mcp_util import PolygonAPI, analyze_stock_query, extract_ticker, save_analysis_report

# Load environment variables
load_dotenv()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

class FinanceOutput(BaseModel):
    """Output model for finance validation"""
    is_about_finance: bool
    reasoning: str

class FinancialAnalysisAgent:
    """Financial Analysis Agent using OpenAI"""
    
    def __init__(self, openai_client: AsyncOpenAI, polygon_api: PolygonAPI):
        self.client = openai_client
        self.polygon = polygon_api
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")  # Configurable model with default
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
        You are a finance query validator. Determine if the user's query is related to finance, stocks, markets, or investments.
        
        Finance-related topics include: stock prices, company analysis, market trends, financial news, trading, investments, economic indicators, earnings, dividends, market cap, etc.
        
        Respond with JSON format: {"is_about_finance": boolean, "reasoning": "explanation"}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": guardrail_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return FinanceOutput(**result)
        except Exception as e:
            return FinanceOutput(
                is_about_finance=False, 
                reasoning=f"Error in validation: {str(e)}"
            )
    
    async def analyze_with_ai(self, query: str, polygon_data: str) -> str:
        """Generate AI-powered analysis using OpenAI"""
        analysis_prompt = f"""
        {self.system_prompt}
        
        User Query: {query}
        
        Polygon.io Data:
        {polygon_data}
        
        Provide a comprehensive financial analysis based on the data above. Include:
        - Key insights about the stock/company
        - Analysis of price movements and trends
        - Relevant context from news
        - Risk factors to consider
        - Investment considerations
        
        Always end with the disclaimer: "Not financial advice. For informational purposes only."
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": analysis_prompt}],
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error generating AI analysis: {str(e)}"

@st.cache_resource
def initialize_apis():
    """Initialize OpenAI and Polygon APIs"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    
    if not openai_api_key:
        st.error("❌ OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
        st.stop()
    
    if not polygon_api_key:
        st.error("❌ Polygon API key not found. Please set POLYGON_API_KEY in your environment.")
        st.stop()
    
    openai_client = AsyncOpenAI(api_key=openai_api_key)
    polygon_api = PolygonAPI(polygon_api_key)
    
    return FinancialAnalysisAgent(openai_client, polygon_api)

def main():
    st.title("📈 Polygon.io AI Chat")
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
        
        # Show current model configuration
        current_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        st.markdown(f"**Current AI Model:** `{current_model}`")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize agent
    agent = initialize_apis()
    
    # Example queries as buttons in main area (only show if no messages)
    if not st.session_state.messages:
        st.markdown("### 💡 Try these example queries:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Get the latest price of Microsoft", use_container_width=True):
                st.session_state.example_query = "Get the latest price of Microsoft"
                st.rerun()
            if st.button("🍎 Do a deep dive on AAPL over the last year", use_container_width=True):
                st.session_state.example_query = "Do a deep dive on AAPL over the last year"
                st.rerun()
        
        with col2:
            if st.button("🚗 Compare TSLA and NVDA performance", use_container_width=True):
                st.session_state.example_query = "Compare TSLA and NVDA performance"
                st.rerun()
            if st.button("📰 What's the latest news on META?", use_container_width=True):
                st.session_state.example_query = "What's the latest news on META?"
                st.rerun()
        
        st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle example query if set
    if hasattr(st.session_state, 'example_query') and st.session_state.example_query:
        prompt = st.session_state.example_query
        st.session_state.example_query = None  # Clear it
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing query..."):
                try:
                    # Validate finance query
                    validation = asyncio.run(agent.validate_finance_query(prompt))
                    
                    if not validation.is_about_finance:
                        error_msg = f"❌ This query doesn't appear to be finance-related. {validation.reasoning}\n\nPlease ask questions about stocks, market data, financial analysis, or related topics."
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    else:
                        # Get Polygon data
                        polygon_data = analyze_stock_query(prompt, agent.polygon)
                        
                        # Generate AI analysis
                        ai_analysis = asyncio.run(agent.analyze_with_ai(prompt, polygon_data))
                        
                        # Combine responses
                        full_response = f"{polygon_data}\n\n## 🤖 AI Analysis\n\n{ai_analysis}"
                        
                        st.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        
                        # Offer to save report
                        ticker = extract_ticker(prompt)
                        if ticker and st.button(f"💾 Save {ticker} Report"):
                            filepath = save_analysis_report(full_response, ticker)
                            st.success(f"Report saved to: {filepath}")
                
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me about stocks, market data, or financial analysis..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing query..."):
                try:
                    # Validate finance query
                    validation = asyncio.run(agent.validate_finance_query(prompt))
                    
                    if not validation.is_about_finance:
                        error_msg = f"❌ This query doesn't appear to be finance-related. {validation.reasoning}\n\nPlease ask questions about stocks, market data, financial analysis, or related topics."
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    else:
                        # Get Polygon data
                        polygon_data = analyze_stock_query(prompt, agent.polygon)
                        
                        # Generate AI analysis
                        ai_analysis = asyncio.run(agent.analyze_with_ai(prompt, polygon_data))
                        
                        # Combine responses
                        full_response = f"{polygon_data}\n\n## 🤖 AI Analysis\n\n{ai_analysis}"
                        
                        st.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        
                        # Offer to save report
                        ticker = extract_ticker(prompt)
                        if ticker and st.button(f"💾 Save {ticker} Report"):
                            filepath = save_analysis_report(full_response, ticker)
                            st.success(f"Report saved to: {filepath}")
                
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()

