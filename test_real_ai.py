#!/usr/bin/env python3
"""
Test AI Analysis with Anthropic API using .env file
This script loads the .env file and tests Claude AI analysis
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from analysis.ai_analysis import analyze_stock_with_ai, analyze_portfolio_with_ai

def test_env_loading():
    """Test if .env file is loaded and API key is available"""
    print("🔑 Testing .env File Loading")
    print("=" * 50)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        print("\n📝 Please check your .env file contains:")
        print("   ANTHROPIC_API_KEY=your-actual-api-key-here")
        return False
    
    if api_key == 'your-anthropic-api-key-here' or len(api_key) < 10:
        print("❌ Please replace the placeholder with your actual API key in .env")
        return False
    
    print(f"✅ API key loaded from .env: {api_key[:8]}...{api_key[-4:]}")
    return True

def test_real_ai_analysis():
    """Test real AI analysis with Claude"""
    print("\n🤖 Testing Real AI Analysis with Claude")
    print("=" * 50)
    
    try:
        print("🔍 Analyzing AAPL with Anthropic Claude...")
        result = analyze_stock_with_ai("AAPL", provider="anthropic")
        
        print("📊 Claude AI Analysis Results:")
        print(f"   Symbol: {result['symbol']}")
        print(f"   Recommendation: {result['recommendation']}")
        print(f"   Confidence: {result['confidence']*100:.1f}%")
        print(f"   Timestamp: {result['timestamp']}")
        
        print(f"\n📈 Investment Summary:")
        print(f"   {result['summary'][:300]}...")
        
        print(f"\n💡 Key AI Insights ({len(result['key_insights'])} total):")
        for i, insight in enumerate(result['key_insights'][:3], 1):
            print(f"   {i}. {insight['type'].upper()}")
            print(f"      → {insight['recommendation']}")
            print(f"      → Confidence: {insight['confidence']*100:.1f}%")
            print(f"      → Reasoning: {insight['reasoning'][:120]}...")
            print()
        
        print(f"⚠️ Risk Factors ({len(result['risk_factors'])} identified):")
        for i, risk in enumerate(result['risk_factors'][:3], 1):
            print(f"   {i}. {risk}")
        
        print(f"\n🚀 Growth Opportunities ({len(result['opportunities'])} identified):")
        for i, opp in enumerate(result['opportunities'][:3], 1):
            print(f"   {i}. {opp}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI analysis: {e}")
        print("💡 This could be due to:")
        print("   • Invalid API key")
        print("   • Network connectivity issues") 
        print("   • API rate limits or quota issues")
        return False

def test_portfolio_ai():
    """Test portfolio analysis with Claude"""
    print("\n\n🏢 Testing Portfolio AI Analysis")
    print("=" * 50)
    
    portfolio = {
        "AAPL": 0.3,
        "MSFT": 0.25, 
        "GOOGL": 0.2,
        "TSLA": 0.15,
        "NVDA": 0.1
    }
    
    try:
        print(f"📊 Analyzing portfolio: {list(portfolio.keys())}")
        result = analyze_portfolio_with_ai(portfolio, provider="anthropic")
        
        print("🤖 Claude Portfolio Analysis:")
        print(f"   Summary: {result['summary'][:200]}...")
        
        print(f"\n💡 Portfolio Insights ({len(result['key_insights'])} total):")
        for i, insight in enumerate(result['key_insights'][:2], 1):
            print(f"   {i}. {insight['type']}: {insight['recommendation']}")
            print(f"      → {insight['reasoning'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Portfolio analysis error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AI Investment Analysis - Anthropic Claude Testing")
    print("=" * 60)
    print("Testing real AI analysis with your Anthropic API key from .env file")
    
    # Test .env loading
    if not test_env_loading():
        return False
    
    # Test stock analysis
    stock_success = test_real_ai_analysis()
    
    # Test portfolio analysis
    portfolio_success = test_portfolio_ai()
    
    print("\n" + "=" * 60)
    if stock_success and portfolio_success:
        print("🎉 All AI Tests Successful!")
        print("✅ Claude AI integration is working perfectly")
        print("✅ Real investment insights are being generated")
        print("✅ API key configuration is correct")
        
        print("\n🎯 Next Steps:")
        print("• Test via FastAPI: GET /v1/analysis/ai/AAPL?provider=anthropic")
        print("• Try different stocks and time periods")
        print("• Compare analysis from different providers")
        print("• Use in production applications")
        
        return True
    else:
        print("⚠️ Some tests failed - please check your setup")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🌟 Anthropic Claude AI Analysis Ready!")
    else:
        print("\n❌ Please resolve issues before proceeding")