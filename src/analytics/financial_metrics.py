"""
Financial metrics computation engine
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FinancialMetrics:
    """Container for computed financial metrics"""
    company_cik: str
    period_end: date
    metrics: Dict[str, float]
    ratios: Dict[str, float]
    computed_at: datetime


class FinancialMetricsEngine:
    """Engine for computing financial metrics and ratios"""
    
    def __init__(self):
        self.metric_definitions = self._load_metric_definitions()
    
    def _load_metric_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load financial metric calculation definitions"""
        return {
            # Liquidity Ratios
            "current_ratio": {
                "formula": "current_assets / current_liabilities",
                "description": "Measures ability to pay short-term obligations",
                "components": ["current_assets", "current_liabilities"]
            },
            "quick_ratio": {
                "formula": "(current_assets - inventory) / current_liabilities",
                "description": "Liquidity ratio excluding inventory",
                "components": ["current_assets", "inventory", "current_liabilities"]
            },
            "cash_ratio": {
                "formula": "cash_and_equivalents / current_liabilities",
                "description": "Most conservative liquidity ratio",
                "components": ["cash_and_equivalents", "current_liabilities"]
            },
            
            # Profitability Ratios
            "gross_margin": {
                "formula": "(revenue - cost_of_goods_sold) / revenue * 100",
                "description": "Gross profit as percentage of revenue",
                "components": ["revenue", "cost_of_goods_sold"]
            },
            "operating_margin": {
                "formula": "operating_income / revenue * 100",
                "description": "Operating profit as percentage of revenue",
                "components": ["operating_income", "revenue"]
            },
            "net_margin": {
                "formula": "net_income / revenue * 100",
                "description": "Net profit as percentage of revenue",
                "components": ["net_income", "revenue"]
            },
            "roa": {
                "formula": "net_income / total_assets * 100",
                "description": "Return on Assets",
                "components": ["net_income", "total_assets"]
            },
            "roe": {
                "formula": "net_income / shareholders_equity * 100",
                "description": "Return on Equity",
                "components": ["net_income", "shareholders_equity"]
            },
            
            # Efficiency Ratios
            "asset_turnover": {
                "formula": "revenue / total_assets",
                "description": "How efficiently assets generate revenue",
                "components": ["revenue", "total_assets"]
            },
            "inventory_turnover": {
                "formula": "cost_of_goods_sold / inventory",
                "description": "How quickly inventory is sold",
                "components": ["cost_of_goods_sold", "inventory"]
            },
            "receivables_turnover": {
                "formula": "revenue / accounts_receivable",
                "description": "How quickly receivables are collected",
                "components": ["revenue", "accounts_receivable"]
            },
            
            # Leverage Ratios
            "debt_to_equity": {
                "formula": "total_debt / shareholders_equity",
                "description": "Financial leverage ratio",
                "components": ["total_debt", "shareholders_equity"]
            },
            "debt_to_assets": {
                "formula": "total_debt / total_assets",
                "description": "Percentage of assets financed by debt",
                "components": ["total_debt", "total_assets"]
            },
            "interest_coverage": {
                "formula": "operating_income / interest_expense",
                "description": "Ability to pay interest on debt",
                "components": ["operating_income", "interest_expense"]
            },
            
            # Market Ratios (require market data)
            "price_to_earnings": {
                "formula": "market_price_per_share / earnings_per_share",
                "description": "P/E ratio",
                "components": ["market_price_per_share", "earnings_per_share"]
            },
            "price_to_book": {
                "formula": "market_price_per_share / book_value_per_share",
                "description": "P/B ratio",
                "components": ["market_price_per_share", "book_value_per_share"]
            },
            "dividend_yield": {
                "formula": "annual_dividend_per_share / market_price_per_share * 100",
                "description": "Dividend yield percentage",
                "components": ["annual_dividend_per_share", "market_price_per_share"]
            }
        }
    
    def normalize_line_item_name(self, line_item: str) -> str:
        """Normalize financial statement line item names"""
        # Common mappings for different reporting standards
        mappings = {
            # Revenue variations
            "total_revenue": "revenue",
            "net_revenue": "revenue",
            "sales": "revenue",
            "net_sales": "revenue",
            
            # Assets
            "total_current_assets": "current_assets",
            "cash_and_cash_equivalents": "cash_and_equivalents",
            "cash": "cash_and_equivalents",
            
            # Liabilities
            "total_current_liabilities": "current_liabilities",
            "current_liabilities_total": "current_liabilities",
            
            # Equity
            "total_stockholders_equity": "shareholders_equity",
            "stockholders_equity": "shareholders_equity",
            "total_shareholders_equity": "shareholders_equity",
            
            # Income statement
            "total_operating_expenses": "operating_expenses",
            "income_from_operations": "operating_income",
            "operating_profit": "operating_income",
            "net_earnings": "net_income",
            "profit": "net_income",
            
            # Debt
            "long_term_debt": "total_debt",
            "total_liabilities": "total_debt"
        }
        
        normalized = line_item.lower().replace(" ", "_").replace("-", "_")
        return mappings.get(normalized, normalized)
    
    def extract_financial_data(self, financial_statements: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract and normalize financial data from statements"""
        data = {}
        
        for statement in financial_statements:
            line_item = self.normalize_line_item_name(statement["line_item"])
            value = statement.get("value")
            
            if value is not None and isinstance(value, (int, float)):
                data[line_item] = float(value)
        
        return data
    
    def compute_metrics(self, financial_data: Dict[str, float]) -> Dict[str, float]:
        """Compute financial metrics from raw financial data"""
        computed_metrics = {}
        
        for metric_name, definition in self.metric_definitions.items():
            try:
                # Check if all required components are available
                components = definition["components"]
                if all(component in financial_data for component in components):
                    
                    # Safely compute the metric
                    result = self._safe_compute_metric(metric_name, financial_data)
                    if result is not None:
                        computed_metrics[metric_name] = result
                        
                else:
                    missing = [comp for comp in components if comp not in financial_data]
                    logger.debug(f"Cannot compute {metric_name}: missing {missing}")
            
            except Exception as e:
                logger.error(f"Error computing {metric_name}: {str(e)}")
        
        return computed_metrics
    
    def _safe_compute_metric(self, metric_name: str, data: Dict[str, float]) -> Optional[float]:
        """Safely compute a single metric with error handling"""
        try:
            if metric_name == "current_ratio":
                if data["current_liabilities"] != 0:
                    return data["current_assets"] / data["current_liabilities"]
            
            elif metric_name == "quick_ratio":
                if data["current_liabilities"] != 0:
                    quick_assets = data["current_assets"] - data.get("inventory", 0)
                    return quick_assets / data["current_liabilities"]
            
            elif metric_name == "cash_ratio":
                if data["current_liabilities"] != 0:
                    return data["cash_and_equivalents"] / data["current_liabilities"]
            
            elif metric_name == "gross_margin":
                if data["revenue"] != 0:
                    gross_profit = data["revenue"] - data.get("cost_of_goods_sold", 0)
                    return (gross_profit / data["revenue"]) * 100
            
            elif metric_name == "operating_margin":
                if data["revenue"] != 0:
                    return (data["operating_income"] / data["revenue"]) * 100
            
            elif metric_name == "net_margin":
                if data["revenue"] != 0:
                    return (data["net_income"] / data["revenue"]) * 100
            
            elif metric_name == "roa":
                if data["total_assets"] != 0:
                    return (data["net_income"] / data["total_assets"]) * 100
            
            elif metric_name == "roe":
                if data["shareholders_equity"] != 0:
                    return (data["net_income"] / data["shareholders_equity"]) * 100
            
            elif metric_name == "asset_turnover":
                if data["total_assets"] != 0:
                    return data["revenue"] / data["total_assets"]
            
            elif metric_name == "inventory_turnover":
                if data.get("inventory", 0) != 0:
                    return data.get("cost_of_goods_sold", 0) / data["inventory"]
            
            elif metric_name == "receivables_turnover":
                if data.get("accounts_receivable", 0) != 0:
                    return data["revenue"] / data["accounts_receivable"]
            
            elif metric_name == "debt_to_equity":
                if data["shareholders_equity"] != 0:
                    return data["total_debt"] / data["shareholders_equity"]
            
            elif metric_name == "debt_to_assets":
                if data["total_assets"] != 0:
                    return data["total_debt"] / data["total_assets"]
            
            elif metric_name == "interest_coverage":
                if data.get("interest_expense", 0) != 0:
                    return data["operating_income"] / data["interest_expense"]
            
            elif metric_name == "price_to_earnings":
                if data.get("earnings_per_share", 0) != 0:
                    return data.get("market_price_per_share", 0) / data["earnings_per_share"]
            
            elif metric_name == "price_to_book":
                if data.get("book_value_per_share", 0) != 0:
                    return data.get("market_price_per_share", 0) / data["book_value_per_share"]
            
            elif metric_name == "dividend_yield":
                if data.get("market_price_per_share", 0) != 0:
                    dividend = data.get("annual_dividend_per_share", 0)
                    return (dividend / data["market_price_per_share"]) * 100
            
            return None
            
        except (ZeroDivisionError, TypeError, KeyError) as e:
            logger.warning(f"Error computing {metric_name}: {str(e)}")
            return None
    
    def analyze_metric_trends(self, historical_metrics: List[FinancialMetrics]) -> Dict[str, Dict[str, Any]]:
        """Analyze trends in financial metrics over time"""
        if len(historical_metrics) < 2:
            return {}
        
        # Sort by period_end
        sorted_metrics = sorted(historical_metrics, key=lambda x: x.period_end)
        
        trend_analysis = {}
        
        # Get all metric names
        all_metrics = set()
        for fm in sorted_metrics:
            all_metrics.update(fm.metrics.keys())
        
        for metric_name in all_metrics:
            values = []
            dates = []
            
            for fm in sorted_metrics:
                if metric_name in fm.metrics:
                    values.append(fm.metrics[metric_name])
                    dates.append(fm.period_end)
            
            if len(values) < 2:
                continue
            
            # Calculate trend metrics
            latest_value = values[-1]
            previous_value = values[-2]
            first_value = values[0]
            
            # Period-over-period change
            pop_change = ((latest_value - previous_value) / abs(previous_value)) * 100 if previous_value != 0 else 0
            
            # Total change from first to last
            total_change = ((latest_value - first_value) / abs(first_value)) * 100 if first_value != 0 else 0
            
            # Average value
            avg_value = np.mean(values)
            
            # Volatility (standard deviation)
            volatility = np.std(values) if len(values) > 1 else 0
            
            # Trend direction
            if len(values) >= 3:
                # Simple linear trend
                x = np.arange(len(values))
                z = np.polyfit(x, values, 1)
                trend_slope = z[0]
                
                if abs(trend_slope) < 0.01:
                    trend_direction = "stable"
                elif trend_slope > 0:
                    trend_direction = "improving"
                else:
                    trend_direction = "declining"
            else:
                trend_direction = "improving" if pop_change > 0 else "declining"
            
            trend_analysis[metric_name] = {
                "latest_value": latest_value,
                "previous_value": previous_value,
                "period_over_period_change": pop_change,
                "total_change": total_change,
                "average_value": avg_value,
                "volatility": volatility,
                "trend_direction": trend_direction,
                "data_points": len(values)
            }
        
        return trend_analysis
    
    def benchmark_against_industry(self, company_metrics: Dict[str, float], 
                                  industry_metrics: Dict[str, List[float]]) -> Dict[str, Dict[str, Any]]:
        """Benchmark company metrics against industry averages"""
        benchmarks = {}
        
        for metric_name, company_value in company_metrics.items():
            if metric_name in industry_metrics:
                industry_values = industry_metrics[metric_name]
                
                if len(industry_values) > 0:
                    industry_median = np.median(industry_values)
                    industry_mean = np.mean(industry_values)
                    industry_std = np.std(industry_values)
                    
                    # Percentile ranking
                    percentile = (np.sum(np.array(industry_values) <= company_value) / len(industry_values)) * 100
                    
                    # Z-score
                    z_score = (company_value - industry_mean) / industry_std if industry_std > 0 else 0
                    
                    # Performance assessment
                    if percentile >= 75:
                        performance = "excellent"
                    elif percentile >= 50:
                        performance = "above_average"
                    elif percentile >= 25:
                        performance = "below_average"
                    else:
                        performance = "poor"
                    
                    benchmarks[metric_name] = {
                        "company_value": company_value,
                        "industry_median": industry_median,
                        "industry_mean": industry_mean,
                        "percentile_rank": percentile,
                        "z_score": z_score,
                        "performance": performance,
                        "sample_size": len(industry_values)
                    }
        
        return benchmarks
    
    def get_metric_interpretation(self, metric_name: str, value: float) -> Dict[str, str]:
        """Get interpretation and context for a metric value"""
        interpretation = {
            "metric_name": metric_name,
            "value": value,
            "description": self.metric_definitions.get(metric_name, {}).get("description", ""),
            "interpretation": "",
            "recommendation": ""
        }
        
        # Add specific interpretations based on metric type and value
        if metric_name == "current_ratio":
            if value > 2.5:
                interpretation["interpretation"] = "Very high liquidity, possibly inefficient use of assets"
                interpretation["recommendation"] = "Consider investing excess cash in growth opportunities"
            elif value > 1.5:
                interpretation["interpretation"] = "Good liquidity position"
                interpretation["recommendation"] = "Maintain current liquidity management"
            elif value > 1.0:
                interpretation["interpretation"] = "Adequate liquidity"
                interpretation["recommendation"] = "Monitor cash flow closely"
            else:
                interpretation["interpretation"] = "Potential liquidity concerns"
                interpretation["recommendation"] = "Improve working capital management"
        
        elif metric_name == "debt_to_equity":
            if value > 2.0:
                interpretation["interpretation"] = "High leverage, higher financial risk"
                interpretation["recommendation"] = "Consider reducing debt levels"
            elif value > 1.0:
                interpretation["interpretation"] = "Moderate leverage"
                interpretation["recommendation"] = "Monitor debt service capabilities"
            elif value > 0.5:
                interpretation["interpretation"] = "Conservative capital structure"
                interpretation["recommendation"] = "Could potentially use more leverage for growth"
            else:
                interpretation["interpretation"] = "Very conservative financing"
                interpretation["recommendation"] = "Consider optimal capital structure"
        
        elif metric_name in ["gross_margin", "operating_margin", "net_margin"]:
            if value > 20:
                interpretation["interpretation"] = "Strong profitability"
                interpretation["recommendation"] = "Maintain competitive advantages"
            elif value > 10:
                interpretation["interpretation"] = "Healthy margins"
                interpretation["recommendation"] = "Look for efficiency improvements"
            elif value > 5:
                interpretation["interpretation"] = "Adequate profitability"
                interpretation["recommendation"] = "Focus on cost management"
            else:
                interpretation["interpretation"] = "Margin pressure"
                interpretation["recommendation"] = "Urgent need for operational improvements"
        
        return interpretation