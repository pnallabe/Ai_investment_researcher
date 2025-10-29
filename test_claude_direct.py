#!/usr/bin/env python3
"""
Simple Anthropic API Test
Direct test of Anthropic API with your key
"""

import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

def test_anthropic_direct():
    """Direct test of Anthropic API"""
    print("🧪 Direct Anthropic API Test")
    print("=" * 40)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No API key found in .env")
        return False
    
    print(f"✅ API Key loaded: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        # Initialize client
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Client initialized")
        
        # Simple test message
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            temperature=0,
            messages=[
                {"role": "user", "content": "What is Apple Inc's stock symbol?"}
            ]
        )
        
        response = message.content[0].text
        print(f"✅ API Response: {response}")
        
        if "AAPL" in response:
            print("🎉 Anthropic API is working perfectly!")
            return True
        else:
            print("⚠️ API responded but answer seems unexpected")
            return False
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

def test_investment_analysis():
    """Test investment analysis with Anthropic"""
    print("\n🏦 Investment Analysis Test")
    print("=" * 40)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return False
        
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = """
Analyze Apple Inc. (AAPL) as an investment opportunity. Provide:
1. Overall recommendation (BUY/HOLD/SELL)
2. Key strengths and weaknesses
3. Risk level (LOW/MEDIUM/HIGH)

Keep response under 200 words.
"""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            temperature=0.3,
            system="You are an expert financial analyst providing investment advice.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = message.content[0].text
        print("📊 Claude Investment Analysis:")
        print(analysis)
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Anthropic Claude API Testing")
    print("=" * 50)
    
    # Test 1: Basic API connection
    basic_success = test_anthropic_direct()
    
    if basic_success:
        # Test 2: Investment analysis
        analysis_success = test_investment_analysis()
        
        if analysis_success:
            print("\n🌟 All tests passed! Claude is ready for investment analysis.")
        else:
            print("\n⚠️ Basic API works but investment analysis had issues.")
    else:
        print("\n❌ Basic API test failed. Check your API key and network connection.")