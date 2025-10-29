"""
Time series forecasting module for financial data
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ForecastMethod(Enum):
    """Available forecasting methods"""
    SIMPLE_MOVING_AVERAGE = "sma"
    EXPONENTIAL_SMOOTHING = "exp_smooth"
    LINEAR_REGRESSION = "linear_regression"
    ARIMA = "arima"
    SEASONAL_DECOMPOSITION = "seasonal"


@dataclass
class ForecastResult:
    """Container for forecast results"""
    method: str
    forecast_values: List[float]
    forecast_dates: List[date]
    confidence_intervals: Optional[List[Tuple[float, float]]] = None
    metrics: Optional[Dict[str, float]] = None
    model_parameters: Optional[Dict[str, Any]] = None


class TimeSeriesForecaster:
    """Time series forecasting engine for financial data"""
    
    def __init__(self):
        self.supported_methods = [method.value for method in ForecastMethod]
    
    def prepare_time_series(self, data_points: List[Dict[str, Any]], 
                           value_column: str, date_column: str) -> pd.DataFrame:
        """Prepare time series data for forecasting"""
        try:
            df = pd.DataFrame(data_points)
            
            # Convert date column to datetime
            df[date_column] = pd.to_datetime(df[date_column])
            
            # Sort by date
            df = df.sort_values(date_column)
            
            # Set date as index
            df.set_index(date_column, inplace=True)
            
            # Ensure numeric values
            df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
            
            # Remove any missing values
            df = df.dropna(subset=[value_column])
            
            logger.info(f"Prepared time series with {len(df)} data points")
            return df
            
        except Exception as e:
            logger.error(f"Error preparing time series data: {str(e)}")
            return pd.DataFrame()
    
    def simple_moving_average(self, df: pd.DataFrame, value_column: str,
                            periods: int = 5, forecast_periods: int = 12) -> ForecastResult:
        """Simple moving average forecast"""
        try:
            values = df[value_column].values
            
            # Calculate moving average
            if len(values) < periods:
                logger.warning(f"Insufficient data for {periods}-period moving average")
                periods = max(2, len(values) // 2)
            
            # Simple moving average of last 'periods' values
            ma_value = np.mean(values[-periods:])
            
            # Generate forecast (assuming constant value)
            forecast_values = [ma_value] * forecast_periods
            
            # Generate forecast dates
            last_date = df.index[-1]
            forecast_dates = []
            for i in range(1, forecast_periods + 1):
                if isinstance(last_date, pd.Timestamp):
                    next_date = last_date + pd.DateOffset(months=i)
                    forecast_dates.append(next_date.date())
                else:
                    forecast_dates.append(last_date + timedelta(days=30*i))
            
            # Calculate simple accuracy metrics on historical data
            if len(values) > periods:
                historical_predictions = []
                actuals = []
                
                for i in range(periods, len(values)):
                    pred = np.mean(values[i-periods:i])
                    historical_predictions.append(pred)
                    actuals.append(values[i])
                
                mae = np.mean(np.abs(np.array(historical_predictions) - np.array(actuals)))
                rmse = np.sqrt(np.mean((np.array(historical_predictions) - np.array(actuals))**2))
                
                metrics = {"mae": mae, "rmse": rmse, "periods_used": periods}
            else:
                metrics = {"periods_used": periods}
            
            return ForecastResult(
                method="simple_moving_average",
                forecast_values=forecast_values,
                forecast_dates=forecast_dates,
                metrics=metrics,
                model_parameters={"periods": periods}
            )
            
        except Exception as e:
            logger.error(f"Error in simple moving average forecast: {str(e)}")
            return self._empty_forecast_result("simple_moving_average")
    
    def exponential_smoothing(self, df: pd.DataFrame, value_column: str,
                            alpha: float = 0.3, forecast_periods: int = 12) -> ForecastResult:
        """Exponential smoothing forecast"""
        try:
            values = df[value_column].values
            
            if len(values) < 2:
                logger.warning("Insufficient data for exponential smoothing")
                return self._empty_forecast_result("exponential_smoothing")
            
            # Initialize
            smoothed = [values[0]]
            
            # Calculate exponentially smoothed values
            for i in range(1, len(values)):
                smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[i-1]
                smoothed.append(smoothed_value)
            
            # Forecast (assuming trend continues)
            last_smoothed = smoothed[-1]
            
            # Simple trend calculation
            if len(smoothed) >= 2:
                trend = smoothed[-1] - smoothed[-2]
            else:
                trend = 0
            
            forecast_values = []
            for i in range(forecast_periods):
                forecast_value = last_smoothed + trend * (i + 1)
                forecast_values.append(forecast_value)
            
            # Generate forecast dates
            last_date = df.index[-1]
            forecast_dates = []
            for i in range(1, forecast_periods + 1):
                if isinstance(last_date, pd.Timestamp):
                    next_date = last_date + pd.DateOffset(months=i)
                    forecast_dates.append(next_date.date())
                else:
                    forecast_dates.append(last_date + timedelta(days=30*i))
            
            # Calculate accuracy metrics
            if len(values) > 1:
                predictions = smoothed[1:]  # Skip first value (initialization)
                actuals = values[1:]
                
                mae = np.mean(np.abs(np.array(predictions) - np.array(actuals)))
                rmse = np.sqrt(np.mean((np.array(predictions) - np.array(actuals))**2))
                
                metrics = {"mae": mae, "rmse": rmse, "alpha": alpha}
            else:
                metrics = {"alpha": alpha}
            
            return ForecastResult(
                method="exponential_smoothing",
                forecast_values=forecast_values,
                forecast_dates=forecast_dates,
                metrics=metrics,
                model_parameters={"alpha": alpha, "trend": trend}
            )
            
        except Exception as e:
            logger.error(f"Error in exponential smoothing forecast: {str(e)}")
            return self._empty_forecast_result("exponential_smoothing")
    
    def linear_regression_forecast(self, df: pd.DataFrame, value_column: str,
                                 forecast_periods: int = 12) -> ForecastResult:
        """Linear regression forecast"""
        try:
            values = df[value_column].values
            
            if len(values) < 3:
                logger.warning("Insufficient data for linear regression")
                return self._empty_forecast_result("linear_regression")
            
            # Prepare data for regression
            x = np.arange(len(values)).reshape(-1, 1)
            y = values
            
            # Simple linear regression (y = mx + b)
            n = len(values)
            x_mean = np.mean(x.flatten())
            y_mean = np.mean(y)
            
            # Calculate slope and intercept
            numerator = np.sum((x.flatten() - x_mean) * (y - y_mean))
            denominator = np.sum((x.flatten() - x_mean) ** 2)
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
            else:
                slope = 0
                intercept = y_mean
            
            # Generate forecasts
            forecast_values = []
            for i in range(forecast_periods):
                x_future = len(values) + i
                forecast_value = slope * x_future + intercept
                forecast_values.append(forecast_value)
            
            # Generate forecast dates
            last_date = df.index[-1]
            forecast_dates = []
            for i in range(1, forecast_periods + 1):
                if isinstance(last_date, pd.Timestamp):
                    next_date = last_date + pd.DateOffset(months=i)
                    forecast_dates.append(next_date.date())
                else:
                    forecast_dates.append(last_date + timedelta(days=30*i))
            
            # Calculate R-squared and other metrics
            y_pred = slope * x.flatten() + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - y_mean) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            mae = np.mean(np.abs(y - y_pred))
            rmse = np.sqrt(np.mean((y - y_pred) ** 2))
            
            metrics = {
                "r_squared": r_squared,
                "mae": mae,
                "rmse": rmse,
                "slope": slope,
                "intercept": intercept
            }
            
            return ForecastResult(
                method="linear_regression",
                forecast_values=forecast_values,
                forecast_dates=forecast_dates,
                metrics=metrics,
                model_parameters={"slope": slope, "intercept": intercept}
            )
            
        except Exception as e:
            logger.error(f"Error in linear regression forecast: {str(e)}")
            return self._empty_forecast_result("linear_regression")
    
    def seasonal_decomposition_forecast(self, df: pd.DataFrame, value_column: str,
                                      period: int = 4, forecast_periods: int = 12) -> ForecastResult:
        """Simple seasonal forecast using seasonal patterns"""
        try:
            values = df[value_column].values
            
            if len(values) < period * 2:
                logger.warning(f"Insufficient data for seasonal analysis (need at least {period * 2} points)")
                return self._empty_forecast_result("seasonal_decomposition")
            
            # Calculate seasonal components (simple approach)
            seasonal_components = []
            
            # Group values by season
            for season in range(period):
                season_values = []
                for i in range(season, len(values), period):
                    season_values.append(values[i])
                
                if season_values:
                    seasonal_components.append(np.mean(season_values))
                else:
                    seasonal_components.append(0)
            
            # Calculate trend (simple linear trend)
            x = np.arange(len(values))
            trend_slope = np.polyfit(x, values, 1)[0] if len(values) > 1 else 0
            
            # Generate forecasts
            forecast_values = []
            last_value = values[-1]
            
            for i in range(forecast_periods):
                # Trend component
                trend_component = trend_slope * (i + 1)
                
                # Seasonal component
                season_index = (len(values) + i) % period
                seasonal_component = seasonal_components[season_index]
                
                # Base level (average of recent non-seasonal values)
                recent_values = values[-min(period, len(values)):]
                base_level = np.mean(recent_values)
                
                # Combine components
                forecast_value = base_level + trend_component + (seasonal_component - np.mean(seasonal_components))
                forecast_values.append(forecast_value)
            
            # Generate forecast dates
            last_date = df.index[-1]
            forecast_dates = []
            for i in range(1, forecast_periods + 1):
                if isinstance(last_date, pd.Timestamp):
                    next_date = last_date + pd.DateOffset(months=i)
                    forecast_dates.append(next_date.date())
                else:
                    forecast_dates.append(last_date + timedelta(days=30*i))
            
            # Simple accuracy metrics
            mae = np.std(values) * 0.5  # Rough estimate
            metrics = {
                "period": period,
                "trend_slope": trend_slope,
                "estimated_mae": mae,
                "seasonal_strength": np.std(seasonal_components)
            }
            
            return ForecastResult(
                method="seasonal_decomposition",
                forecast_values=forecast_values,
                forecast_dates=forecast_dates,
                metrics=metrics,
                model_parameters={
                    "period": period,
                    "seasonal_components": seasonal_components,
                    "trend_slope": trend_slope
                }
            )
            
        except Exception as e:
            logger.error(f"Error in seasonal decomposition forecast: {str(e)}")
            return self._empty_forecast_result("seasonal_decomposition")
    
    def ensemble_forecast(self, df: pd.DataFrame, value_column: str,
                         methods: List[str] = None, forecast_periods: int = 12) -> ForecastResult:
        """Ensemble forecast combining multiple methods"""
        try:
            if methods is None:
                methods = ["simple_moving_average", "exponential_smoothing", "linear_regression"]
            
            forecasts = []
            weights = []
            
            # Generate individual forecasts
            for method in methods:
                if method == "simple_moving_average":
                    result = self.simple_moving_average(df, value_column, forecast_periods=forecast_periods)
                elif method == "exponential_smoothing":
                    result = self.exponential_smoothing(df, value_column, forecast_periods=forecast_periods)
                elif method == "linear_regression":
                    result = self.linear_regression_forecast(df, value_column, forecast_periods=forecast_periods)
                elif method == "seasonal_decomposition":
                    result = self.seasonal_decomposition_forecast(df, value_column, forecast_periods=forecast_periods)
                else:
                    continue
                
                if result.forecast_values:
                    forecasts.append(result.forecast_values)
                    
                    # Weight based on accuracy (lower error = higher weight)
                    if result.metrics and "mae" in result.metrics:
                        weight = 1 / (result.metrics["mae"] + 1e-10)  # Avoid division by zero
                    else:
                        weight = 1.0
                    weights.append(weight)
            
            if not forecasts:
                return self._empty_forecast_result("ensemble")
            
            # Normalize weights
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            # Calculate weighted average forecast
            ensemble_forecast = []
            for i in range(forecast_periods):
                weighted_sum = sum(forecasts[j][i] * weights[j] for j in range(len(forecasts)))
                ensemble_forecast.append(weighted_sum)
            
            # Generate forecast dates (use the first successful method's dates)
            if methods and methods[0] in ["simple_moving_average", "exponential_smoothing", "linear_regression"]:
                first_result = self.simple_moving_average(df, value_column, forecast_periods=forecast_periods)
                forecast_dates = first_result.forecast_dates
            else:
                last_date = df.index[-1]
                forecast_dates = []
                for i in range(1, forecast_periods + 1):
                    if isinstance(last_date, pd.Timestamp):
                        next_date = last_date + pd.DateOffset(months=i)
                        forecast_dates.append(next_date.date())
                    else:
                        forecast_dates.append(last_date + timedelta(days=30*i))
            
            metrics = {
                "methods_used": len(forecasts),
                "method_names": methods,
                "weights": weights
            }
            
            return ForecastResult(
                method="ensemble",
                forecast_values=ensemble_forecast,
                forecast_dates=forecast_dates,
                metrics=metrics,
                model_parameters={"methods": methods, "weights": weights}
            )
            
        except Exception as e:
            logger.error(f"Error in ensemble forecast: {str(e)}")
            return self._empty_forecast_result("ensemble")
    
    def forecast_stock_price(self, price_data: List[Dict[str, Any]], 
                           forecast_periods: int = 30, method: str = "ensemble") -> ForecastResult:
        """Forecast stock prices"""
        try:
            df = self.prepare_time_series(price_data, "close_price", "date")
            
            if df.empty:
                return self._empty_forecast_result(method)
            
            if method == "ensemble":
                return self.ensemble_forecast(df, "close_price", forecast_periods=forecast_periods)
            elif method == "simple_moving_average":
                return self.simple_moving_average(df, "close_price", forecast_periods=forecast_periods)
            elif method == "exponential_smoothing":
                return self.exponential_smoothing(df, "close_price", forecast_periods=forecast_periods)
            elif method == "linear_regression":
                return self.linear_regression_forecast(df, "close_price", forecast_periods=forecast_periods)
            elif method == "seasonal_decomposition":
                return self.seasonal_decomposition_forecast(df, "close_price", forecast_periods=forecast_periods)
            else:
                logger.error(f"Unknown forecasting method: {method}")
                return self._empty_forecast_result(method)
            
        except Exception as e:
            logger.error(f"Error forecasting stock price: {str(e)}")
            return self._empty_forecast_result(method)
    
    def forecast_financial_metric(self, metric_data: List[Dict[str, Any]], 
                                metric_name: str, forecast_periods: int = 4,
                                method: str = "linear_regression") -> ForecastResult:
        """Forecast financial metrics (typically quarterly)"""
        try:
            df = self.prepare_time_series(metric_data, metric_name, "period_end")
            
            if df.empty:
                return self._empty_forecast_result(method)
            
            if method == "seasonal_decomposition":
                return self.seasonal_decomposition_forecast(df, metric_name, period=4, forecast_periods=forecast_periods)
            elif method == "linear_regression":
                return self.linear_regression_forecast(df, metric_name, forecast_periods=forecast_periods)
            elif method == "exponential_smoothing":
                return self.exponential_smoothing(df, metric_name, forecast_periods=forecast_periods)
            else:
                return self.simple_moving_average(df, metric_name, forecast_periods=forecast_periods)
            
        except Exception as e:
            logger.error(f"Error forecasting financial metric: {str(e)}")
            return self._empty_forecast_result(method)
    
    def _empty_forecast_result(self, method: str) -> ForecastResult:
        """Return empty forecast result"""
        return ForecastResult(
            method=method,
            forecast_values=[],
            forecast_dates=[],
            metrics={"error": "Forecast failed"},
            model_parameters={}
        )
    
    def validate_forecast_accuracy(self, historical_data: List[Dict[str, Any]],
                                 value_column: str, date_column: str,
                                 test_periods: int = 6, method: str = "ensemble") -> Dict[str, float]:
        """Validate forecast accuracy using historical data"""
        try:
            if len(historical_data) < test_periods + 10:
                logger.warning("Insufficient data for forecast validation")
                return {}
            
            # Split data into train and test
            train_data = historical_data[:-test_periods]
            test_data = historical_data[-test_periods:]
            
            # Create forecast on training data
            train_df = self.prepare_time_series(train_data, value_column, date_column)
            
            if method == "ensemble":
                forecast_result = self.ensemble_forecast(train_df, value_column, forecast_periods=test_periods)
            elif method == "linear_regression":
                forecast_result = self.linear_regression_forecast(train_df, value_column, forecast_periods=test_periods)
            else:
                forecast_result = self.simple_moving_average(train_df, value_column, forecast_periods=test_periods)
            
            if not forecast_result.forecast_values:
                return {}
            
            # Compare with actual values
            actual_values = [point[value_column] for point in test_data]
            predicted_values = forecast_result.forecast_values[:len(actual_values)]
            
            # Calculate accuracy metrics
            mae = np.mean(np.abs(np.array(predicted_values) - np.array(actual_values)))
            rmse = np.sqrt(np.mean((np.array(predicted_values) - np.array(actual_values))**2))
            
            # Mean Absolute Percentage Error
            mape = np.mean(np.abs((np.array(actual_values) - np.array(predicted_values)) / np.array(actual_values))) * 100
            
            # Directional accuracy (percentage of correct directional predictions)
            correct_directions = 0
            for i in range(1, len(actual_values)):
                actual_direction = 1 if actual_values[i] > actual_values[i-1] else -1
                predicted_direction = 1 if predicted_values[i] > predicted_values[i-1] else -1
                
                if actual_direction == predicted_direction:
                    correct_directions += 1
            
            directional_accuracy = (correct_directions / max(1, len(actual_values) - 1)) * 100
            
            return {
                "mae": mae,
                "rmse": rmse,
                "mape": mape,
                "directional_accuracy": directional_accuracy,
                "test_periods": len(actual_values),
                "method": method
            }
            
        except Exception as e:
            logger.error(f"Error validating forecast accuracy: {str(e)}")
            return {}