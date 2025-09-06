#!/usr/bin/env python3
"""
Debug script to check model configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Environment Variables ===")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT_SET')[:20]}...")
print(f"POLYGON_API_KEY: {os.getenv('POLYGON_API_KEY', 'NOT_SET')}")
print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'NOT_SET')}")

print("\n=== Model Configuration Test ===")
model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
print(f"Model to use: '{model}'")
print(f"Model length: {len(model)}")
print(f"Model repr: {repr(model)}")

# Test if there are any hidden characters
for i, char in enumerate(model):
    print(f"  Char {i}: '{char}' (ord: {ord(char)})")

print("\n=== Allowed Models ===")
allowed = ["gpt-4.1-mini", "gpt-4.1-nano", "gemini-2.5-flash"]
for allowed_model in allowed:
    match = model == allowed_model
    print(f"  {allowed_model}: {'✓' if match else '✗'}")

