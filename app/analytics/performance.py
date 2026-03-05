import numpy as np
import pandas as pd

class PerformanceAnalytics:
    @staticmethod
    def calculate_returns(prices_df, column='Close'):
        """Calculate daily returns from price dataframe"""
        if prices_df is None or prices_df.empty or column not in prices_df.columns:
            return pd.Series(dtype=float)
            
        data = prices_df[column]
        # In case a dataframe is selected (e.g. duplicate columns), squeeze it to a Series
        if isinstance(data, pd.DataFrame):
            data = data.iloc[:, 0]
            
        return data.pct_change().dropna()

    @staticmethod
    def calculate_cumulative_return(returns):
        """Calculate cumulative return series"""
        if returns.empty:
            return returns
        return (1 + returns).cumprod() - 1

    @staticmethod
    def get_annualized_return(returns, periods_per_year=252):
        """Calculate annualized return"""
        if returns.empty:
            return 0.0
        comp_ret = (1 + returns).prod()
        n_periods = len(returns)
        if n_periods == 0:
            return 0.0
        return comp_ret ** (periods_per_year / n_periods) - 1

    @staticmethod
    def get_annualized_volatility(returns, periods_per_year=252):
        """Calculate annualized volatility"""
        if returns.empty:
            return 0.0
        return returns.std() * np.sqrt(periods_per_year)

    @staticmethod
    def get_sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
        """Calculate annualized Sharpe ratio"""
        if returns.empty:
            return 0.0
        ann_ret = PerformanceAnalytics.get_annualized_return(returns, periods_per_year)
        ann_vol = PerformanceAnalytics.get_annualized_volatility(returns, periods_per_year)
        if ann_vol == 0:
            return 0.0
        return (ann_ret - risk_free_rate) / ann_vol

    @staticmethod
    def get_max_drawdown(returns):
        """Calculate maximum drawdown"""
        if returns.empty:
            return 0.0
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.cummax()
        drawdown = cum_returns / rolling_max - 1
        return drawdown.min()

    @staticmethod
    def calculate_beta(asset_returns, benchmark_returns):
        """Calculate Beta against benchmark"""
        try:
            # Align dates
            df = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
            if df.empty or len(df) < 2:
                return 1.0 # default to 1
                
            cov = np.cov(df.iloc[:, 0], df.iloc[:, 1])[0][1]
            var_bench = np.var(df.iloc[:, 1])
            if var_bench == 0:
                return 1.0
            return cov / var_bench
        except Exception:
            return 1.0

    @staticmethod
    def calculate_alpha(asset_returns, benchmark_returns, risk_free_rate=0.0):
        """Calculate Jensen's Alpha annualized"""
        try:
            beta = PerformanceAnalytics.calculate_beta(asset_returns, benchmark_returns)
            ann_ret_asset = PerformanceAnalytics.get_annualized_return(asset_returns)
            ann_ret_bench = PerformanceAnalytics.get_annualized_return(benchmark_returns)
            
            # Alpha = R_p - [R_f + Beta * (R_m - R_f)]
            alpha = ann_ret_asset - (risk_free_rate + beta * (ann_ret_bench - risk_free_rate))
            return alpha
        except Exception:
            return 0.0

    @staticmethod
    def calculate_correlation(returns_df):
        """Calculate correlation matrix for multiple assets"""
        if returns_df.empty:
            return returns_df
        return returns_df.corr()

    @staticmethod
    def calculate_historical_var(returns, confidence_level=0.95):
        """Calculate Historical Value at Risk (VaR)"""
        if returns.empty or len(returns) < 30: # Need sufficient data points
            return 0.0
        # VaR is typically expressed as a positive number representing loss
        return -np.percentile(returns, (1 - confidence_level) * 100)

    @staticmethod
    def calculate_cvar(returns, confidence_level=0.95):
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        if returns.empty or len(returns) < 30:
            return 0.0
        var = -PerformanceAnalytics.calculate_historical_var(returns, confidence_level)
        # Calculate mean of returns worse than VaR
        tail_returns = returns[returns <= var]
        if tail_returns.empty:
             return 0.0
        return -tail_returns.mean()
        
    @staticmethod
    def calculate_capture_ratios(asset_returns, benchmark_returns):
        """Calculate Up and Down Market Capture Ratios"""
        try:
            df = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
            if df.empty or len(df) < 2:
                return {"up_capture": 1.0, "down_capture": 1.0}
            
            asset = df.iloc[:, 0]
            bench = df.iloc[:, 1]
            
            # Up market: periods where benchmark return > 0
            up_market = df[bench > 0]
            if not up_market.empty:
                up_asset_ret = PerformanceAnalytics.get_annualized_return(up_market.iloc[:, 0])
                up_bench_ret = PerformanceAnalytics.get_annualized_return(up_market.iloc[:, 1])
                up_capture = up_asset_ret / up_bench_ret if up_bench_ret != 0 else 1.0
            else:
                up_capture = 1.0
                
            # Down market: periods where benchmark return <= 0
            down_market = df[bench <= 0]
            if not down_market.empty:
                down_asset_ret = PerformanceAnalytics.get_annualized_return(down_market.iloc[:, 0])
                down_bench_ret = PerformanceAnalytics.get_annualized_return(down_market.iloc[:, 1])
                down_capture = down_asset_ret / down_bench_ret if down_bench_ret != 0 else 1.0
            else:
                down_capture = 1.0
                
            return {
                "up_capture": up_capture,
                "down_capture": down_capture
            }
        except Exception:
            return {"up_capture": 1.0, "down_capture": 1.0}

    @staticmethod
    def run_monte_carlo_simulation(initial_value, mu, sigma, days=252, simulations=1000, seed=42):
        """
        Run Monte Carlo simulation using Geometric Brownian Motion
        Returns a DataFrame of potential price paths
        """
        if pd.isna(mu) or pd.isna(sigma) or sigma <= 0:
            return pd.DataFrame()
            
        np.random.seed(seed)
        
        # Calculate daily drift and volatility (assuming inputs are annualized)
        daily_mu = mu / 252.0
        daily_sigma = sigma / np.sqrt(252.0)
        
        # Generate random shocks
        dt = 1 # 1 day step
        shocks = np.random.normal(0, 1, (days, simulations))
        
        # Calculate daily returns using geometric brownian motion standard formula
        dr = np.exp((daily_mu - 0.5 * daily_sigma**2) * dt + daily_sigma * shocks * np.sqrt(dt))
        
        # Generate price paths
        price_paths = np.zeros_like(dr)
        price_paths[0] = initial_value
        
        for t in range(1, days):
             price_paths[t] = price_paths[t-1] * dr[t]
             
        return pd.DataFrame(price_paths)
