import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class YFinanceService:
    @staticmethod
    def _safe_float(val):
        """Safely parse various string formats from yfinance into floats"""
        if pd.isnull(val):
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        
        # Clean string: yfinance sometimes returns weird strings like '6.625.754.803.452.95'
        # We'll take everything up to the second decimal point if multiple exist
        val_str = str(val).replace(',', '').replace('%', '').strip()
        parts = val_str.split('.')
        if len(parts) > 2:
            val_str = parts[0] + '.' + ''.join(parts[1:])
            
        try:
            # If original had a % sign, it's often 6.62, which we need as 0.0662
            parsed = float(val_str)
            return parsed / 100.0 if '%' in str(val) else parsed
        except:
            return 0.0

    @staticmethod
    def get_price_history(ticker, start_date=None, end_date=None, interval="1d"):
        """Fetch historical price data from yfinance"""
        try:
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
            if data.empty:
                return pd.DataFrame()
            
            # yfinance sometimes returns MultiIndex columns (e.g. ('Close', 'VTI'))
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_current_price(ticker):
        """Fetch current price data"""
        try:
            ticker_obj = yf.Ticker(ticker)
            # Use fast_info if available, else history
            info = ticker_obj.fast_info
            if info and 'last_price' in info:
                return info['last_price']
            
            hist = ticker_obj.history(period="1d")
            if not hist.empty:
                return hist['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Error getting current price for {ticker}: {e}")
            return None

    @staticmethod
    def get_etf_profile(ticker):
        """Fetch ETF profile details"""
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            profile = {
                "ticker": ticker,
                "name": info.get("longName"),
                "issuer": info.get("fundFamily"),
                "asset_class": info.get("quoteType"),
                "expense_ratio": info.get("feesExpensesInvestment", info.get("annualReportExpenseRatio")),
                "aum": info.get("totalAssets", info.get("marketCap")),
                "inception_date": info.get("fundInceptionDate"),
                "benchmark": info.get("category"),
                "currency": info.get("currency"),
                "exchange": info.get("exchange"),
                "ytd_return": info.get("ytdReturn"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow")
            }
            return profile
        except Exception as e:
            print(f"Error getting ETF profile for {ticker}: {e}")
            return {}

    @staticmethod
    def get_etf_holdings(ticker):
        """Fetch top 10 holdings with weights"""
        try:
            ticker_obj = yf.Ticker(ticker)
            
            # Check for the new funds_data object in recent yfinance versions
            if hasattr(ticker_obj, 'funds_data'):
                fd = ticker_obj.funds_data
                if fd and hasattr(fd, 'top_holdings'):
                    df = fd.top_holdings
                    if df is not None and not df.empty:
                        res = []
                        for idx, row in df.head(10).iterrows():
                            val = row.get('Holding Percent', 0)
                            safe_val = YFinanceService._safe_float(val)
                            res.append({
                                "symbol": idx,
                                "holdingName": row.get('Name', idx),
                                "holdingPercent": safe_val
                            })
                        return res
            
            # Fallback legacy methods
            info = ticker_obj.info
            holdings = info.get('holdings', [])
            if holdings:
                # Ensure percent is float safely
                for h in holdings:
                    h['holdingPercent'] = YFinanceService._safe_float(h.get('holdingPercent', 0))
                return sorted(holdings, key=lambda x: x.get('holdingPercent', 0), reverse=True)[:10]
                
            if hasattr(ticker_obj, 'fund_top_holdings'):
                df = ticker_obj.fund_top_holdings
                if df is not None and not df.empty:
                    res = []
                    for idx, row in df.head(10).iterrows():
                        val = row.get('weight', 0)
                        safe_val = YFinanceService._safe_float(val)
                        res.append({
                            "symbol": idx,
                            "holdingName": row.get('name', idx),
                            "holdingPercent": safe_val
                        })
                    return res
                    
            return []
        except Exception as e:
            print(f"Error getting holdings for {ticker}: {e}")
            return []

    @staticmethod
    def get_etf_sectors(ticker):
        """Fetch GICS sector exposure"""
        try:
            ticker_obj = yf.Ticker(ticker)
            
            # Use the new funds_data object
            if hasattr(ticker_obj, 'funds_data'):
                fd = ticker_obj.funds_data
                if fd and hasattr(fd, 'sector_weightings'):
                    sectors = fd.sector_weightings
                    if sectors and isinstance(sectors, dict) and len(sectors) > 0:
                        return sectors
            
            # Fallback legacy direct method
            if hasattr(ticker_obj, 'fund_sector_weightings'):
                df = ticker_obj.fund_sector_weightings
                if df is not None and not df.empty:
                    res = {}
                    for idx, row in df.iterrows():
                        val = row.iloc[0] if isinstance(row, pd.Series) else row
                        res[idx] = float(val) if pd.notnull(val) else 0.0
                    return res
                    
            # Fallback info dict
            info = ticker_obj.info
            sectors = info.get('sectorWeightings', [])
            if sectors:
                res = {}
                for s in sectors:
                    for k, v in s.items():
                        res[k] = v
                return res
                
            return {}
        except Exception as e:
            print(f"Error getting sectors for {ticker}: {e}")
            return {}

    @staticmethod
    def get_etf_geography(ticker):
        """Fetch geographical breakdown"""
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            # Usually in info['fundProfile']['feesExpensesInvestment'] etc...
            # yfinance geographical info can be spotty.
            # Currently it's often not directly exposed in a clean dict, but occasionally under 'geographicRegion'
            regions = info.get('geographicRegion', [])
            if not regions:
                 # Fallback to an empty dict. In production, we'd use AlphaVantage/FMP for this
                return {}
            
            # If it's a list, it might be a list of dicts or just strings.
            res = {}
            if isinstance(regions, list):
                for r in regions:
                    if isinstance(r, dict):
                        for k, v in r.items():
                            res[k] = v
                    elif isinstance(r, str):
                        res[r] = 0.0 # Placeholder if only names are given
            return res
        except Exception as e:
            print(f"Error getting geography for {ticker}: {e}")
            return {}
