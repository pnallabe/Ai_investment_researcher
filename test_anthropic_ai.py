#!/usr/bin/env python3
"""
Test AI Analysis with Real Anthropic API
This script tests the AI analysis system with Claude for real investment insights
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from analysis.ai_analysis import analyze_stock_with_ai, analyze_portfolio_with_ai, LLMProvider

def test_anthropic_setup():
    """Test if Anthropic API key is properly configured"""
    print("🔑 Testing Anthropic API Configuration")
    print("=" * 50)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("\n📝 To set up your API key:")
        print("   export ANTHROPIC_API_KEY='your-api-key-here'")
        print("   # Then run this script again")
        return False
    
    if api_key == 'your-anthropic-api-key-here' or len(api_key) < 10:
        print("❌ Please replace the placeholder with your actual API key")
        return False
    
    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
    print("✅ Anthropic configuration looks good!")
    return True

def test_anthropic_stock_analysis():
    """Test real AI stock analysis with Claude"""
    print("\n\n🤖 Real AI Stock Analysis with Claude")
    print("=" * 50)
    
    print("🔍 Analyzing AAPL with Anthropic Claude...")
    try:
        # Use Anthropic provider for real AI analysis
        result = analyze_stock_with_ai("AAPL", provider="anthropic")
        
        print("📊 Claude AI Analysis Results:")
        print(f"   Symbol: {result['symbol']}")
        print(f"   Recommendation: {result['recommendation']}")
        print(f"   Confidence: {result['confidence']*100:.1f}%")
        print(f"   Summary: {result['summary'][:200]}...")
        
        print(f"\n💡 AI Insights ({len(result['key_insights'])} total):")
        for i, insight in enumerate(result['key_insights'][:3], 1):
            print(f"   {i}. {insight['type']}: {insight['recommendation']}")
            print(f"      Reasoning: {insight['reasoning'][:150]}...")
            print(f"      Confidence: {insight['confidence']*100:.1f}%")
        
        print(f"\n⚠️ Risk Factors ({len(result['risk_factors'])} total):")
        for i, risk in enumerate(result['risk_factors'][:3], 1):
            print(f"   {i}. {risk}")
        
        print(f"\n🚀 Opportunities ({len(result['opportunities'])} total):")
        for i, opportunity in enumerate(result['opportunities'][:3], 1):
            print(f"   {i}. {opportunity}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing Anthropic analysis: {e}")
        print("💡 This might be due to API key issues or network connectivity")
        return None

def test_anthropic_portfolio_analysis():
    """Test real AI portfolio analysis with Claude"""
    print("\n\n🏢 Real AI Portfolio Analysis with Claude")
    print("=" * 50)
    
    portfolio = {
        "AAPL": 0.3,
        "MSFT": 0.25,
        "GOOGL": 0.2,
        "TSLA": 0.15,
        "NVDA": 0.1
    }
    
    print(f"🏢 Analyzing portfolio: {list(portfolio.keys())}")
    
    try:
        result = analyze_portfolio_with_ai(portfolio, provider="anthropic")
        
        print("📊 Claude Portfolio Analysis:")
        print(f"   Portfolio: {list(result['portfolio'].keys())}")
        print(f"   Summary: {result['summary'][:200]}...")
        
        print(f"\n💡 AI Portfolio Insights ({len(result['key_insights'])} total):")
        for i, insight in enumerate(result['key_insights'][:2], 1):
            print(f"   {i}. {insight['type']}: {insight['recommendation']}")
            print(f"      Reasoning: {insight['reasoning'][:150]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in portfolio analysis: {e}")
        return None

def compare_providers():
    """Compare analysis from different providers"""
    print("\n\n⚖️ Provider Comparison: Mock vs Anthropic")
    print("=" * 50)
    
    symbol = "AAPL"
    
    # Test mock provider
    print("🔍 Mock Provider Analysis:")
    mock_result = analyze_stock_with_ai(symbol, provider="mock")
    print(f"   Recommendation: {mock_result['recommendation']}")
    print(f"   Confidence: {mock_result['confidence']*100:.1f}%")
    print(f"   Summary: {mock_result['summary'][:100]}...")
    
    # Test Anthropic provider
    print("\n🔍 Anthropic Claude Analysis:")
    try:
        anthropic_result = analyze_stock_with_ai(symbol, provider="anthropic")
        print(f"   Recommendation: {anthropic_result['recommendation']}")
        print(f"   Confidence: {anthropic_result['confidence']*100:.1f}%")
        print(f"   Summary: {anthropic_result['summary'][:100]}...")
        
        print("\n🎯 Key Differences:")
        print(f"   Mock: Simple fallback analysis")
        print(f"   Claude: {len(anthropic_result['key_insights'])} detailed insights with reasoning")
        
    except Exception as e:
        print(f"   ❌ Anthropic analysis failed: {e}")

def main():
    """Run comprehensive Anthropic API testing"""
    print("🚀 AI Analysis Testing with Anthropic Claude")
    print("=" * 60)
    print("This script tests the AI analysis system with your Anthropic API key")
    print("for real investment insights powered by Claude.")
    
    # Step 1: Check API key setup
    if not test_anthropic_setup():
        print("\n⚠️ Setup required before testing can proceed")
        return False
    
    # Step 2: Test stock analysis
    stock_result = test_anthropic_stock_analysis()
    
    # Step 3: Test portfolio analysis  
    portfolio_result = test_anthropic_portfolio_analysis()
    
    # Step 4: Compare providers
    compare_providers()
    
    print("\n\n🎉 Anthropic AI Testing Complete!")
    print("=" * 60)
    
    if stock_result and portfolio_result:
        print("✅ All Tests Passed:")
        print("  🔍 Stock Analysis with Claude: Working")
        print("  🏢 Portfolio Analysis with Claude: Working")
        print("  🤖 Real AI Investment Insights: Available")
        print("  📊 Professional-grade Analysis: Ready")
        
        print(f"\n🌟 Next Steps:")
        print(f"  • Use provider='anthropic' in API calls")
        print(f"  • Test via FastAPI: GET /v1/analysis/ai/AAPL?provider=anthropic")
        print(f"  • Try different stocks and portfolio compositions")
        print(f"  • Compare insights from different AI providers")
        
        return True
    else:
        print("⚠️ Some tests had issues:")
        print("  • Check your API key is valid and has credits")
        print("  • Verify network connectivity")
        print("  • Try again or contact support if problems persist")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🌟 Anthropic AI Analysis Ready for Production!")
    else:
        print("\n⚠️ Please resolve setup issues before proceeding")