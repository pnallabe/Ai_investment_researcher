"""
Portfolio Risk Analysis Engine

This module provides comprehensive portfolio risk analysis including:
- Portfolio Risk Metrics (Sharpe Ratio, Beta, VaR)
- Correlation Analysis
- Diversification Analysis
- Risk-Adjusted Returns
- Monte Carlo Simulations
- Portfolio Optimization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import yfinance as yf
from datetime import datetime, timedelta
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class PortfolioRiskAnalyzer:
    """Main class for performing portfolio risk analysis"""
    
    def __init__(self, portfolio: Dict[str, float], benchmark: str = "^GSPC", period: str = "1y"):
        """
        Initialize Portfolio Risk Analyzer
        
        Args:
            portfolio: Dictionary with stock symbols as keys and weights as values
            benchmark: Benchmark index symbol (default: S&P 500)
            period: Data period for analysis
        """
        self.portfolio = portfolio
        self.benchmark = benchmark
        self.period = period
        self.symbols = list(portfolio.keys())
        self.weights = np.array(list(portfolio.values()))
        
        # Ensure weights sum to 1
        if not np.isclose(self.weights.sum(), 1.0):
            print(f"Warning: Weights sum to {self.weights.sum():.4f}, normalizing to 1.0")
            self.weights = self.weights / self.weights.sum()
        
        self.data = {}
        self.returns = pd.DataFrame()
        self.portfolio_returns = pd.Series()
        self.benchmark_returns = pd.Series()
        self._fetch_data()
    
    def _fetch_data(self) -> None:
        """Fetch stock data and calculate returns"""
        try:
            # Fetch portfolio data
            all_symbols = self.symbols + [self.benchmark]
            
            for symbol in all_symbols:
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period=self.period)
                if not hist_data.empty:
                    self.data[symbol] = hist_data
            
            # Calculate returns
            self._calculate_returns()
            
        except Exception as e:
            print(f"Error fetching data: {e}")
    
    def _calculate_returns(self) -> None:
        """Calculate daily returns for all assets"""
        returns_data = {}
        
        # Calculate returns for portfolio stocks
        for symbol in self.symbols:
            if symbol in self.data and not self.data[symbol].empty:
                price_data = self.data[symbol]['Close']
                returns_data[symbol] = price_data.pct_change().dropna()
        
        self.returns = pd.DataFrame(returns_data)
        
        # Calculate portfolio returns
        if not self.returns.empty:
            self.portfolio_returns = (self.returns * self.weights).sum(axis=1)
        
        # Calculate benchmark returns
        if self.benchmark in self.data and not self.data[self.benchmark].empty:
            benchmark_prices = self.data[self.benchmark]['Close']
            self.benchmark_returns = benchmark_prices.pct_change().dropna()
    
    def calculate_portfolio_statistics(self) -> Dict[str, float]:
        """
        Calculate basic portfolio statistics
        
        Returns:
            Dictionary with portfolio statistics
        """
        if self.portfolio_returns.empty:
            return {}
        
        stats = {}
        
        # Annualized return
        annual_return = self.portfolio_returns.mean() * 252
        stats['annual_return'] = annual_return
        
        # Annualized volatility
        annual_volatility = self.portfolio_returns.std() * np.sqrt(252)
        stats['annual_volatility'] = annual_volatility
        
        # Sharpe Ratio (assuming 0% risk-free rate)
        stats['sharpe_ratio'] = annual_return / annual_volatility if annual_volatility != 0 else 0
        
        # Maximum Drawdown
        cumulative_returns = (1 + self.portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        stats['max_drawdown'] = drawdowns.min()
        
        # Skewness and Kurtosis
        stats['skewness'] = self.portfolio_returns.skew()
        stats['kurtosis'] = self.portfolio_returns.kurtosis()
        
        return stats
    
    def calculate_beta(self) -> float:
        """
        Calculate portfolio beta relative to benchmark
        
        Returns:
            Portfolio beta
        """
        if self.portfolio_returns.empty or self.benchmark_returns.empty:
            return None
        
        # Align dates
        aligned_data = pd.DataFrame({
            'portfolio': self.portfolio_returns,
            'benchmark': self.benchmark_returns
        }).dropna()
        
        if len(aligned_data) < 20:  # Need sufficient data points
            return None
        
        # Calculate beta using linear regression
        beta = np.cov(aligned_data['portfolio'], aligned_data['benchmark'])[0, 1] / np.var(aligned_data['benchmark'])
        
        return beta
    
    def calculate_var(self, confidence_level: float = 0.05) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR) using multiple methods
        
        Args:
            confidence_level: Confidence level for VaR calculation (default: 5%)
            
        Returns:
            Dictionary with VaR values using different methods
        """
        if self.portfolio_returns.empty:
            return {}
        
        var_results = {}
        
        # Historical VaR
        var_results['historical_var'] = np.percentile(self.portfolio_returns, confidence_level * 100)
        
        # Parametric VaR (assuming normal distribution)
        mean_return = self.portfolio_returns.mean()
        std_return = self.portfolio_returns.std()
        var_results['parametric_var'] = mean_return + std_return * stats.norm.ppf(confidence_level)
        
        # Modified VaR (Cornish-Fisher expansion)
        skewness = self.portfolio_returns.skew()
        kurtosis = self.portfolio_returns.kurtosis()
        z_score = stats.norm.ppf(confidence_level)
        
        modified_z = z_score + (z_score**2 - 1) * skewness / 6 + \
                    (z_score**3 - 3*z_score) * kurtosis / 24 - \
                    (2*z_score**3 - 5*z_score) * skewness**2 / 36
        
        var_results['modified_var'] = mean_return + std_return * modified_z
        
        return var_results
    
    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate correlation matrix for portfolio assets
        
        Returns:
            Correlation matrix DataFrame
        """
        if self.returns.empty:
            return pd.DataFrame()
        
        return self.returns.corr()
    
    def calculate_diversification_metrics(self) -> Dict[str, float]:
        """
        Calculate diversification metrics
        
        Returns:
            Dictionary with diversification metrics
        """
        if self.returns.empty:
            return {}
        
        metrics = {}
        
        # Effective Number of Assets (Herfindahl Index)
        metrics['effective_assets'] = 1 / np.sum(self.weights ** 2)
        
        # Diversification Ratio
        individual_volatilities = self.returns.std() * np.sqrt(252)
        weighted_avg_volatility = np.sum(self.weights * individual_volatilities)
        portfolio_volatility = self.portfolio_returns.std() * np.sqrt(252)
        
        if portfolio_volatility != 0:
            metrics['diversification_ratio'] = weighted_avg_volatility / portfolio_volatility
        else:
            metrics['diversification_ratio'] = 0
        
        # Maximum weight concentration
        metrics['max_weight'] = np.max(self.weights)
        
        # Weight concentration (Gini coefficient)
        sorted_weights = np.sort(self.weights)
        n = len(sorted_weights)
        index = np.arange(1, n + 1)
        metrics['weight_gini'] = (2 * np.sum(sorted_weights * index) / (n * np.sum(sorted_weights))) - (n + 1) / n
        
        return metrics
    
    def monte_carlo_simulation(self, num_simulations: int = 10000, time_horizon: int = 252) -> Dict[str, Any]:
        """
        Perform Monte Carlo simulation for portfolio returns
        
        Args:
            num_simulations: Number of simulation runs
            time_horizon: Time horizon in days (default: 1 year = 252 days)
            
        Returns:
            Dictionary with simulation results
        """
        if self.returns.empty:
            return {}
        
        # Calculate parameters for simulation
        mean_returns = self.returns.mean()
        cov_matrix = self.returns.cov()
        
        # Perform Monte Carlo simulation
        portfolio_results = []
        
        for _ in range(num_simulations):
            # Generate random returns
            random_returns = np.random.multivariate_normal(mean_returns, cov_matrix, time_horizon)
            
            # Calculate portfolio returns
            portfolio_returns = np.sum(random_returns * self.weights, axis=1)
            
            # Calculate cumulative return
            cumulative_return = np.prod(1 + portfolio_returns) - 1
            portfolio_results.append(cumulative_return)
        
        portfolio_results = np.array(portfolio_results)
        
        return {
            'mean_return': np.mean(portfolio_results),
            'std_return': np.std(portfolio_results),
            'percentile_5': np.percentile(portfolio_results, 5),
            'percentile_95': np.percentile(portfolio_results, 95),
            'probability_loss': np.sum(portfolio_results < 0) / num_simulations,
            'all_results': portfolio_results
        }
    
    def calculate_risk_parity_weights(self) -> np.array:
        """
        Calculate risk parity weights where each asset contributes equally to portfolio risk
        
        Returns:
            Array of risk parity weights
        """
        if self.returns.empty:
            return np.array([])
        
        cov_matrix = self.returns.cov().values
        n_assets = len(self.symbols)
        
        def risk_parity_objective(weights):
            """Objective function for risk parity optimization"""
            weights = weights / np.sum(weights)  # Normalize weights
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Risk contributions
            marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            
            # Minimize sum of squared differences from equal risk contribution
            target_contrib = portfolio_vol / n_assets
            return np.sum((contrib - target_contrib) ** 2)
        
        # Constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0.01, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(risk_parity_objective, initial_weights, 
                         method='SLSQP', bounds=bounds, constraints=constraints)
        
        return result.x if result.success else initial_weights
    
    def optimize_portfolio(self, target_return: Optional[float] = None) -> Dict[str, Any]:
        """
        Optimize portfolio using Modern Portfolio Theory
        
        Args:
            target_return: Target annual return (if None, maximize Sharpe ratio)
            
        Returns:
            Dictionary with optimization results
        """
        if self.returns.empty:
            return {}
        
        mean_returns = self.returns.mean() * 252  # Annualized
        cov_matrix = self.returns.cov() * 252  # Annualized
        n_assets = len(self.symbols)
        
        def portfolio_stats(weights):
            """Calculate portfolio statistics"""
            portfolio_return = np.sum(mean_returns * weights)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return portfolio_return, portfolio_vol
        
        def sharpe_ratio(weights):
            """Calculate negative Sharpe ratio (for minimization)"""
            ret, vol = portfolio_stats(weights)
            return -ret / vol if vol != 0 else 0
        
        def portfolio_volatility(weights):
            """Calculate portfolio volatility"""
            return portfolio_stats(weights)[1]
        
        # Constraints and bounds
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        if target_return is not None:
            # Add return constraint
            constraints.append({'type': 'eq', 'fun': lambda x: portfolio_stats(x)[0] - target_return})
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        if target_return is None:
            # Maximize Sharpe ratio
            result = minimize(sharpe_ratio, initial_weights, method='SLSQP', 
                            bounds=bounds, constraints=constraints)
            objective = "Maximum Sharpe Ratio"
        else:
            # Minimize volatility for target return
            result = minimize(portfolio_volatility, initial_weights, method='SLSQP', 
                            bounds=bounds, constraints=constraints)
            objective = f"Minimum Volatility for {target_return:.2%} return"
        
        if result.success:
            optimal_weights = result.x
            opt_return, opt_vol = portfolio_stats(optimal_weights)
            opt_sharpe = opt_return / opt_vol if opt_vol != 0 else 0
            
            return {
                'success': True,
                'objective': objective,
                'optimal_weights': dict(zip(self.symbols, optimal_weights)),
                'expected_return': opt_return,
                'expected_volatility': opt_vol,
                'sharpe_ratio': opt_sharpe
            }
        else:
            return {'success': False, 'message': 'Optimization failed'}
    
    def get_comprehensive_risk_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive portfolio risk analysis
        
        Returns:
            Dictionary with complete risk analysis
        """
        if not self.returns.empty:
            portfolio_stats = self.calculate_portfolio_statistics()
        else:
            portfolio_stats = {}
        
        analysis = {
            'portfolio_composition': dict(zip(self.symbols, self.weights)),
            'analysis_date': datetime.now().isoformat(),
            'portfolio_statistics': portfolio_stats,
            'beta': self.calculate_beta(),
            'value_at_risk': self.calculate_var(),
            'correlation_matrix': self.calculate_correlation_matrix().to_dict() if not self.calculate_correlation_matrix().empty else {},
            'diversification_metrics': self.calculate_diversification_metrics(),
            'monte_carlo_simulation': self.monte_carlo_simulation(1000, 252),  # Reduced for speed
            'risk_parity_weights': dict(zip(self.symbols, self.calculate_risk_parity_weights())) if len(self.calculate_risk_parity_weights()) > 0 else {},
            'optimization_results': {
                'max_sharpe': self.optimize_portfolio(),
                'min_volatility': self.optimize_portfolio(target_return=0.08)  # 8% target return
            },
            'risk_assessment': self._assess_risk_level()
        }
        
        return analysis
    
    def _assess_risk_level(self) -> Dict[str, str]:
        """
        Assess overall portfolio risk level
        
        Returns:
            Dictionary with risk assessment
        """
        assessment = {}
        
        try:
            portfolio_stats = self.calculate_portfolio_statistics()
            diversification_metrics = self.calculate_diversification_metrics()
            
            # Volatility assessment
            annual_vol = portfolio_stats.get('annual_volatility', 0)
            if annual_vol < 0.10:
                vol_risk = "LOW"
            elif annual_vol < 0.20:
                vol_risk = "MODERATE"
            elif annual_vol < 0.30:
                vol_risk = "HIGH"
            else:
                vol_risk = "VERY HIGH"
            
            assessment['volatility_risk'] = vol_risk
            
            # Concentration risk
            max_weight = diversification_metrics.get('max_weight', 0)
            if max_weight < 0.20:
                concentration_risk = "LOW"
            elif max_weight < 0.40:
                concentration_risk = "MODERATE"
            elif max_weight < 0.60:
                concentration_risk = "HIGH"
            else:
                concentration_risk = "VERY HIGH"
            
            assessment['concentration_risk'] = concentration_risk
            
            # Beta risk
            beta = self.calculate_beta()
            if beta is not None:
                if beta < 0.8:
                    beta_risk = "LOW"
                elif beta < 1.2:
                    beta_risk = "MODERATE"
                elif beta < 1.5:
                    beta_risk = "HIGH"
                else:
                    beta_risk = "VERY HIGH"
                
                assessment['market_risk'] = beta_risk
        
        except Exception as e:
            assessment['error'] = str(e)
        
        return assessment

def analyze_multiple_portfolios(portfolios: Dict[str, Dict[str, float]], benchmark: str = "^GSPC") -> Dict[str, Dict]:
    """
    Analyze multiple portfolios for risk metrics
    
    Args:
        portfolios: Dictionary with portfolio names as keys and portfolio compositions as values
        benchmark: Benchmark symbol
        
    Returns:
        Dictionary with risk analysis for each portfolio
    """
    results = {}
    
    for portfolio_name, portfolio_composition in portfolios.items():
        try:
            analyzer = PortfolioRiskAnalyzer(portfolio_composition, benchmark)
            results[portfolio_name] = analyzer.get_comprehensive_risk_analysis()
        except Exception as e:
            results[portfolio_name] = {"error": str(e)}
    
    return results

if __name__ == "__main__":
    # Example usage
    sample_portfolio = {
        'AAPL': 0.3,
        'MSFT': 0.25,
        'GOOGL': 0.2,
        'TSLA': 0.15,
        'NVDA': 0.1
    }
    
    analyzer = PortfolioRiskAnalyzer(sample_portfolio)
    analysis = analyzer.get_comprehensive_risk_analysis()
    
    print("Portfolio Risk Analysis")
    print(f"Annual Return: {analysis['portfolio_statistics'].get('annual_return', 0):.2%}")
    print(f"Annual Volatility: {analysis['portfolio_statistics'].get('annual_volatility', 0):.2%}")
    print(f"Sharpe Ratio: {analysis['portfolio_statistics'].get('sharpe_ratio', 0):.2f}")
    print(f"Beta: {analysis.get('beta', 'N/A')}")
    print(f"Max Drawdown: {analysis['portfolio_statistics'].get('max_drawdown', 0):.2%}")
    print(f"Volatility Risk: {analysis['risk_assessment'].get('volatility_risk', 'N/A')}")
    print(f"Concentration Risk: {analysis['risk_assessment'].get('concentration_risk', 'N/A')}")