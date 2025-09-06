#!/usr/bin/env python3
"""
Test OpenAI API call with the configured model
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

async def test_openai():
    """Test OpenAI API call"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    
    print(f"Testing OpenAI API with model: {model}")
    print(f"API Key: {api_key[:20]}...")
    
    client = AsyncOpenAI(api_key=api_key)
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Is asking about Apple stock price a finance-related query? Respond with JSON: {\"is_about_finance\": true/false, \"reasoning\": \"explanation\"}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=100
        )
        
        print("✅ Success!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_openai())

