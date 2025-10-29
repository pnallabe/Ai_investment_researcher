"""
Advanced Stock Analysis Demo

This script demonstrates all the advanced analysis features including:
- Technical Analysis
- Fundamental Analysis
- Portfolio Risk Analysis
- Multi-stock Comparison
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'analysis'))

from technical_analysis import TechnicalAnalyzer, analyze_multiple_stocks
from fundamental_analysis import FundamentalAnalyzer, analyze_multiple_fundamentals
from portfolio_risk_analysis import PortfolioRiskAnalyzer, analyze_multiple_portfolios
import json
from datetime import datetime

def demo_technical_analysis(symbol="AAPL"):
    """Demo technical analysis features"""
    print(f"\n🔍 Technical Analysis Demo for {symbol}")
    print("=" * 60)
    
    try:
        analyzer = TechnicalAnalyzer(symbol, "1y")
        analysis = analyzer.get_all_indicators()
        
        print(f"Current Price: ${analysis['current_price']:.2f}")
        print(f"RSI (14): {analysis['momentum_indicators']['rsi']:.2f}")
        print(f"MACD Signal: {analysis['signals'].get('macd', 'N/A')}")
        print(f"SMA(20): ${analysis['moving_averages']['sma_20']:.2f}")
        print(f"SMA(50): ${analysis['moving_averages']['sma_50']:.2f}")
        print(f"Bollinger Upper: ${analysis['bollinger_bands']['upper']:.2f}")
        print(f"Bollinger Lower: ${analysis['bollinger_bands']['lower']:.2f}")
        print(f"Trading Signals:")
        for signal_type, signal in analysis['signals'].items():
            print(f"  - {signal_type.upper()}: {signal}")
        
        print("✅ Technical analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Technical analysis error: {e}")

def demo_fundamental_analysis(symbol="AAPL"):
    """Demo fundamental analysis features"""
    print(f"\n📊 Fundamental Analysis Demo for {symbol}")
    print("=" * 60)
    
    try:
        analyzer = FundamentalAnalyzer(symbol)
        analysis = analyzer.get_comprehensive_analysis()
        
        basic_info = analysis['basic_info']
        print(f"Company: {basic_info['company_name']}")
        print(f"Sector: {basic_info['sector']}")
        print(f"Market Cap: ${basic_info['market_cap']:,.0f}")
        
        valuation = analysis['valuation_ratios']
        print(f"\nValuation Metrics:")
        print(f"  P/E Ratio: {valuation.get('pe_ratio', 'N/A')}")
        print(f"  P/B Ratio: {valuation.get('pb_ratio', 'N/A')}")
        print(f"  P/S Ratio: {valuation.get('ps_ratio', 'N/A')}")
        
        profitability = analysis['profitability_ratios']
        print(f"\nProfitability Metrics:")
        print(f"  ROE: {profitability.get('roe', 'N/A')}")
        print(f"  ROA: {profitability.get('roa', 'N/A')}")
        print(f"  Profit Margin: {profitability.get('profit_margin', 'N/A')}")
        
        investment_score = analysis['investment_score']
        print(f"\nInvestment Analysis:")
        print(f"  Score: {investment_score['score']}/100")
        print(f"  Rating: {investment_score['rating']}")
        print(f"  Key Factors: {', '.join(investment_score['factors'][:3])}")
        
        print("✅ Fundamental analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Fundamental analysis error: {e}")

def demo_portfolio_risk_analysis():
    """Demo portfolio risk analysis features"""
    print(f"\n⚖️ Portfolio Risk Analysis Demo")
    print("=" * 60)
    
    try:
        # Sample tech-heavy portfolio
        portfolio = {
            'AAPL': 0.25,
            'MSFT': 0.20,
            'GOOGL': 0.15,
            'TSLA': 0.15,
            'NVDA': 0.10,
            'AMZN': 0.10,
            'META': 0.05
        }
        
        analyzer = PortfolioRiskAnalyzer(portfolio, period="1y")
        analysis = analyzer.get_comprehensive_risk_analysis()
        
        print("Portfolio Composition:")
        for symbol, weight in portfolio.items():
            print(f"  {symbol}: {weight:.1%}")
        
        stats = analysis['portfolio_statistics']
        print(f"\nRisk-Return Metrics:")
        print(f"  Annual Return: {stats['annual_return']:.2%}")
        print(f"  Annual Volatility: {stats['annual_volatility']:.2%}")
        print(f"  Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {stats['max_drawdown']:.2%}")
        print(f"  Beta: {analysis.get('beta', 'N/A')}")
        
        diversification = analysis['diversification_metrics']
        print(f"\nDiversification Analysis:")
        print(f"  Effective Number of Assets: {diversification['effective_assets']:.1f}")
        print(f"  Diversification Ratio: {diversification['diversification_ratio']:.2f}")
        print(f"  Maximum Weight: {diversification['max_weight']:.1%}")
        
        var_data = analysis['value_at_risk']
        print(f"\nValue at Risk (5%):")
        print(f"  Historical VaR: {var_data['historical_var']:.2%}")
        print(f"  Parametric VaR: {var_data['parametric_var']:.2%}")
        
        risk_assessment = analysis['risk_assessment']
        print(f"\nRisk Assessment:")
        print(f"  Volatility Risk: {risk_assessment.get('volatility_risk', 'N/A')}")
        print(f"  Concentration Risk: {risk_assessment.get('concentration_risk', 'N/A')}")
        print(f"  Market Risk (Beta): {risk_assessment.get('market_risk', 'N/A')}")
        
        # Show optimization results
        max_sharpe = analysis['optimization_results']['max_sharpe']
        if max_sharpe.get('success'):
            print(f"\nOptimal Portfolio (Max Sharpe):")
            print(f"  Expected Return: {max_sharpe['expected_return']:.2%}")
            print(f"  Expected Volatility: {max_sharpe['expected_volatility']:.2%}")
            print(f"  Sharpe Ratio: {max_sharpe['sharpe_ratio']:.2f}")
        
        print("✅ Portfolio risk analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Portfolio risk analysis error: {e}")

def demo_multi_stock_comparison():
    """Demo multi-stock comparison features"""
    print(f"\n🏆 Multi-Stock Comparison Demo")
    print("=" * 60)
    
    try:
        symbols = ["AAPL", "MSFT", "GOOGL"]
        
        # Get technical analysis
        technical_results = analyze_multiple_stocks(symbols, "6mo")
        
        # Get fundamental analysis  
        fundamental_results = analyze_multiple_fundamentals(symbols)
        
        print("Stock Comparison Matrix:")
        print(f"{'Metric':<20} {'AAPL':<12} {'MSFT':<12} {'GOOGL':<12}")
        print("-" * 60)
        
        # Compare current prices
        prices = [technical_results[s].get('current_price', 0) for s in symbols]
        print(f"{'Current Price':<20} ${prices[0]:<11.2f} ${prices[1]:<11.2f} ${prices[2]:<11.2f}")
        
        # Compare RSI
        rsi_values = [technical_results[s].get('momentum_indicators', {}).get('rsi', 0) for s in symbols]
        print(f"{'RSI':<20} {rsi_values[0]:<12.1f} {rsi_values[1]:<12.1f} {rsi_values[2]:<12.1f}")
        
        # Compare P/E ratios
        pe_ratios = [fundamental_results[s].get('valuation_ratios', {}).get('pe_ratio', 0) for s in symbols]
        pe_display = [f"{pe:.1f}" if pe else "N/A" for pe in pe_ratios]
        print(f"{'P/E Ratio':<20} {pe_display[0]:<12} {pe_display[1]:<12} {pe_display[2]:<12}")
        
        # Compare investment scores
        scores = [fundamental_results[s].get('investment_score', {}).get('score', 0) for s in symbols]
        print(f"{'Investment Score':<20} {scores[0]:<12.0f} {scores[1]:<12.0f} {scores[2]:<12.0f}")
        
        # Show technical signals
        print(f"\nTechnical Signals:")
        for symbol in symbols:
            signals = technical_results[symbol].get('signals', {})
            trend = signals.get('ma_trend', 'N/A')
            macd = signals.get('macd', 'N/A')
            print(f"  {symbol}: Trend={trend}, MACD={macd}")
        
        print("✅ Multi-stock comparison completed successfully!")
        
    except Exception as e:
        print(f"❌ Multi-stock comparison error: {e}")

def main():
    """Main demo function"""
    print("🚀 Advanced Stock Analysis Demo")
    print("=" * 60)
    print("This demo showcases all advanced analysis features:")
    print("- Technical Analysis (15+ indicators)")
    print("- Fundamental Analysis (financial ratios)")
    print("- Portfolio Risk Analysis (Sharpe, VaR, Monte Carlo)")
    print("- Multi-stock Comparison")
    print()
    print("📊 Starting comprehensive analysis...")
    
    # Run all demos
    demo_technical_analysis("AAPL")
    demo_fundamental_analysis("AAPL")
    demo_portfolio_risk_analysis()
    demo_multi_stock_comparison()
    
    print(f"\n🎉 All analysis demos completed successfully!")
    print(f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Next Steps:")
    print("- Start the FastAPI backend: python mvp_simple.py")
    print("- Test endpoints: http://localhost:8000/docs")
    print("- Try technical analysis: GET /v1/analysis/technical/AAPL")
    print("- Try fundamental analysis: GET /v1/analysis/fundamental/AAPL")
    print("- Try portfolio risk analysis: POST /v1/analysis/portfolio-risk")

if __name__ == "__main__":
    main()