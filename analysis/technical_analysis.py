"""
Technical Analysis Engine for Stock Market Analysis

This module provides comprehensive technical analysis indicators for stock analysis including:
- Moving Averages (SMA, EMA)
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Stochastic Oscillator
- Williams %R
- Volume indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import yfinance as yf
from datetime import datetime, timedelta

class TechnicalAnalyzer:
    """Main class for performing technical analysis on stock data"""
    
    def __init__(self, symbol: str, period: str = "1y"):
        """
        Initialize the Technical Analyzer
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        """
        self.symbol = symbol.upper()
        self.period = period
        self.data = None
        self.indicators = {}
        self._fetch_data()
    
    def _fetch_data(self) -> None:
        """Fetch stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(self.symbol)
            self.data = ticker.history(period=self.period)
            if self.data.empty:
                raise ValueError(f"No data found for symbol {self.symbol}")
        except Exception as e:
            print(f"Error fetching data for {self.symbol}: {e}")
            self.data = pd.DataFrame()
    
    def simple_moving_average(self, period: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA)
        
        Args:
            period: Number of periods for calculation
            
        Returns:
            pandas Series with SMA values
        """
        if self.data.empty:
            return pd.Series()
        
        sma = self.data['Close'].rolling(window=period).mean()
        self.indicators[f'SMA_{period}'] = sma
        return sma
    
    def exponential_moving_average(self, period: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)
        
        Args:
            period: Number of periods for calculation
            
        Returns:
            pandas Series with EMA values
        """
        if self.data.empty:
            return pd.Series()
        
        ema = self.data['Close'].ewm(span=period).mean()
        self.indicators[f'EMA_{period}'] = ema
        return ema
    
    def relative_strength_index(self, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            period: Number of periods for calculation (typically 14)
            
        Returns:
            pandas Series with RSI values (0-100)
        """
        if self.data.empty:
            return pd.Series()
        
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        self.indicators[f'RSI_{period}'] = rsi
        return rsi
    
    def macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            fast_period: Fast EMA period (typically 12)
            slow_period: Slow EMA period (typically 26)
            signal_period: Signal line EMA period (typically 9)
            
        Returns:
            Dictionary with MACD line, signal line, and histogram
        """
        if self.data.empty:
            return {}
        
        ema_fast = self.data['Close'].ewm(span=fast_period).mean()
        ema_slow = self.data['Close'].ewm(span=slow_period).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period).mean()
        histogram = macd_line - signal_line
        
        macd_data = {
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        }
        
        self.indicators['MACD'] = macd_data
        return macd_data
    
    def bollinger_bands(self, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            period: Number of periods for moving average
            std_dev: Number of standard deviations for bands
            
        Returns:
            Dictionary with upper band, middle band (SMA), and lower band
        """
        if self.data.empty:
            return {}
        
        sma = self.data['Close'].rolling(window=period).mean()
        std = self.data['Close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        bb_data = {
            'Upper': upper_band,
            'Middle': sma,
            'Lower': lower_band
        }
        
        self.indicators['BollingerBands'] = bb_data
        return bb_data
    
    def stochastic_oscillator(self, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        Calculate Stochastic Oscillator
        
        Args:
            k_period: Period for %K calculation
            d_period: Period for %D smoothing
            
        Returns:
            Dictionary with %K and %D values
        """
        if self.data.empty:
            return {}
        
        low_min = self.data['Low'].rolling(window=k_period).min()
        high_max = self.data['High'].rolling(window=k_period).max()
        
        k_percent = 100 * ((self.data['Close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        stoch_data = {
            'K_percent': k_percent,
            'D_percent': d_percent
        }
        
        self.indicators['Stochastic'] = stoch_data
        return stoch_data
    
    def williams_r(self, period: int = 14) -> pd.Series:
        """
        Calculate Williams %R
        
        Args:
            period: Number of periods for calculation
            
        Returns:
            pandas Series with Williams %R values (-100 to 0)
        """
        if self.data.empty:
            return pd.Series()
        
        high_max = self.data['High'].rolling(window=period).max()
        low_min = self.data['Low'].rolling(window=period).min()
        
        williams_r = -100 * ((high_max - self.data['Close']) / (high_max - low_min))
        
        self.indicators[f'WilliamsR_{period}'] = williams_r
        return williams_r
    
    def volume_sma(self, period: int = 20) -> pd.Series:
        """
        Calculate Volume Simple Moving Average
        
        Args:
            period: Number of periods for calculation
            
        Returns:
            pandas Series with volume SMA values
        """
        if self.data.empty:
            return pd.Series()
        
        volume_sma = self.data['Volume'].rolling(window=period).mean()
        self.indicators[f'VolumeSMA_{period}'] = volume_sma
        return volume_sma
    
    def price_rate_of_change(self, period: int = 12) -> pd.Series:
        """
        Calculate Price Rate of Change (ROC)
        
        Args:
            period: Number of periods for calculation
            
        Returns:
            pandas Series with ROC values (percentage)
        """
        if self.data.empty:
            return pd.Series()
        
        roc = ((self.data['Close'] - self.data['Close'].shift(period)) / self.data['Close'].shift(period)) * 100
        self.indicators[f'ROC_{period}'] = roc
        return roc
    
    def average_true_range(self, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        
        Args:
            period: Number of periods for calculation
            
        Returns:
            pandas Series with ATR values
        """
        if self.data.empty:
            return pd.Series()
        
        high_low = self.data['High'] - self.data['Low']
        high_close_prev = np.abs(self.data['High'] - self.data['Close'].shift())
        low_close_prev = np.abs(self.data['Low'] - self.data['Close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        atr = true_range.rolling(window=period).mean()
        
        self.indicators[f'ATR_{period}'] = atr
        return atr
    
    def get_all_indicators(self) -> Dict:
        """
        Calculate all technical indicators and return comprehensive analysis
        
        Returns:
            Dictionary with all calculated indicators and current signals
        """
        if self.data.empty:
            return {"error": "No data available"}
        
        # Calculate all indicators
        sma_20 = self.simple_moving_average(20)
        sma_50 = self.simple_moving_average(50)
        ema_12 = self.exponential_moving_average(12)
        ema_26 = self.exponential_moving_average(26)
        rsi = self.relative_strength_index()
        macd_data = self.macd()
        bb_data = self.bollinger_bands()
        stoch_data = self.stochastic_oscillator()
        williams_r = self.williams_r()
        volume_sma = self.volume_sma()
        roc = self.price_rate_of_change()
        atr = self.average_true_range()
        
        current_price = self.data['Close'].iloc[-1]
        
        # Generate trading signals
        signals = self._generate_signals()
        
        return {
            'symbol': self.symbol,
            'current_price': current_price,
            'last_updated': datetime.now().isoformat(),
            'moving_averages': {
                'sma_20': sma_20.iloc[-1] if not sma_20.empty else None,
                'sma_50': sma_50.iloc[-1] if not sma_50.empty else None,
                'ema_12': ema_12.iloc[-1] if not ema_12.empty else None,
                'ema_26': ema_26.iloc[-1] if not ema_26.empty else None,
            },
            'momentum_indicators': {
                'rsi': rsi.iloc[-1] if not rsi.empty else None,
                'williams_r': williams_r.iloc[-1] if not williams_r.empty else None,
                'roc': roc.iloc[-1] if not roc.empty else None,
            },
            'macd': {
                'macd_line': macd_data['MACD'].iloc[-1] if macd_data else None,
                'signal_line': macd_data['Signal'].iloc[-1] if macd_data else None,
                'histogram': macd_data['Histogram'].iloc[-1] if macd_data else None,
            },
            'bollinger_bands': {
                'upper': bb_data['Upper'].iloc[-1] if bb_data else None,
                'middle': bb_data['Middle'].iloc[-1] if bb_data else None,
                'lower': bb_data['Lower'].iloc[-1] if bb_data else None,
            },
            'stochastic': {
                'k_percent': stoch_data['K_percent'].iloc[-1] if stoch_data else None,
                'd_percent': stoch_data['D_percent'].iloc[-1] if stoch_data else None,
            },
            'volume_analysis': {
                'current_volume': self.data['Volume'].iloc[-1],
                'volume_sma_20': volume_sma.iloc[-1] if not volume_sma.empty else None,
            },
            'volatility': {
                'atr': atr.iloc[-1] if not atr.empty else None,
            },
            'signals': signals
        }
    
    def _generate_signals(self) -> Dict[str, str]:
        """
        Generate trading signals based on technical indicators
        
        Returns:
            Dictionary with trading signals for different indicators
        """
        signals = {}
        
        if self.data.empty:
            return signals
        
        current_price = self.data['Close'].iloc[-1]
        
        # RSI signals
        rsi = self.relative_strength_index()
        if not rsi.empty:
            rsi_current = rsi.iloc[-1]
            if rsi_current > 70:
                signals['rsi'] = 'OVERBOUGHT'
            elif rsi_current < 30:
                signals['rsi'] = 'OVERSOLD'
            else:
                signals['rsi'] = 'NEUTRAL'
        
        # Moving Average signals
        sma_20 = self.simple_moving_average(20)
        sma_50 = self.simple_moving_average(50)
        if not sma_20.empty and not sma_50.empty:
            if sma_20.iloc[-1] > sma_50.iloc[-1]:
                signals['ma_trend'] = 'BULLISH'
            else:
                signals['ma_trend'] = 'BEARISH'
        
        # MACD signals
        macd_data = self.macd()
        if macd_data:
            macd_line = macd_data['MACD'].iloc[-1]
            signal_line = macd_data['Signal'].iloc[-1]
            if macd_line > signal_line:
                signals['macd'] = 'BULLISH'
            else:
                signals['macd'] = 'BEARISH'
        
        # Bollinger Bands signals
        bb_data = self.bollinger_bands()
        if bb_data:
            upper = bb_data['Upper'].iloc[-1]
            lower = bb_data['Lower'].iloc[-1]
            if current_price > upper:
                signals['bollinger'] = 'OVERBOUGHT'
            elif current_price < lower:
                signals['bollinger'] = 'OVERSOLD'
            else:
                signals['bollinger'] = 'NEUTRAL'
        
        return signals

def analyze_multiple_stocks(symbols: List[str], period: str = "6mo") -> Dict[str, Dict]:
    """
    Analyze multiple stocks for technical indicators
    
    Args:
        symbols: List of stock symbols
        period: Data period for analysis
        
    Returns:
        Dictionary with analysis for each stock
    """
    results = {}
    
    for symbol in symbols:
        try:
            analyzer = TechnicalAnalyzer(symbol, period)
            results[symbol] = analyzer.get_all_indicators()
        except Exception as e:
            results[symbol] = {"error": str(e)}
    
    return results

if __name__ == "__main__":
    # Example usage
    analyzer = TechnicalAnalyzer("AAPL", "1y")
    analysis = analyzer.get_all_indicators()
    
    print(f"Technical Analysis for {analysis['symbol']}")
    print(f"Current Price: ${analysis['current_price']:.2f}")
    print(f"RSI: {analysis['momentum_indicators']['rsi']:.2f}")
    print(f"MACD Signal: {analysis['signals'].get('macd', 'N/A')}")
    print(f"Overall Trend: {analysis['signals'].get('ma_trend', 'N/A')}")