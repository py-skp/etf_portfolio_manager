import os
from .yfinance_service import YFinanceService
from .cache_service import cache_service

# Optional: financedatabase for searching the universe
try:
    import financedatabase as fd
    fd_available = True
except ImportError:
    fd_available = False

class DataProvider:
    """Unified data provider with caching and provider fallback"""
    
    @staticmethod
    def _get_api_key(key_name):
        """Helper to get API key from session state or environment"""
        import streamlit as st
        if "api_keys" in st.session_state and st.session_state.api_keys.get(key_name):
            return st.session_state.api_keys.get(key_name)
        # Fallback to secrets or env
        return st.secrets.get(key_name, os.environ.get(key_name))

    @staticmethod
    def get_price_history(ticker, start=None, end=None, interval="1d"):
        # Cache key based on ticker and date range
        cache_key = f"price_hist_{ticker}_{start}_{end}_{interval}"
        cached_data = cache_service.get(cache_key)
        if cached_data:
            return cached_data
            
        # Try yfinance (Primary)
        data = YFinanceService.get_price_history(ticker, start, end, interval)
        if not data.empty:
            # Convert to dict for caching
            result = data.to_dict(orient="index")
            # Cache for 1 hour
            cache_service.set(cache_key, result, ttl=3600)
            return result
            
        return {}

    @staticmethod
    def get_current_price(ticker):
        cache_key = f"price_curr_{ticker}"
        cached_price = cache_service.get(cache_key)
        if cached_price:
            return cached_price
            
        price = YFinanceService.get_current_price(ticker)
        if price:
            cache_service.set(cache_key, price, ttl=300) # 5 min cache
            return price
            
        return None

    @staticmethod
    def get_etf_profile(ticker):
        cache_key = f"etf_prof_{ticker}"
        cached_profile = cache_service.get(cache_key)
        if cached_profile:
            return cached_profile
            
        profile = YFinanceService.get_etf_profile(ticker)
        if profile:
            # Cache for 1 week
            cache_service.set(cache_key, profile, ttl=604800)
            return profile
            
        return {}
        
    @staticmethod
    def get_etf_holdings(ticker):
        cache_key = f"etf_holdings_{ticker}"
        cached_holdings = cache_service.get(cache_key)
        if cached_holdings:
            return cached_holdings
            
        holdings = YFinanceService.get_etf_holdings(ticker)
        if holdings:
            cache_service.set(cache_key, holdings, ttl=604800)
            return holdings
            
        return []

    @staticmethod
    def get_etf_sectors(ticker):
        cache_key = f"etf_sectors_{ticker}"
        cached_sectors = cache_service.get(cache_key)
        if cached_sectors:
            return cached_sectors
            
        sectors = YFinanceService.get_etf_sectors(ticker)
        if sectors:
            cache_service.set(cache_key, sectors, ttl=604800)
            return sectors
            
        return {}

    @staticmethod
    def get_etf_geography(ticker):
        cache_key = f"etf_geo_{ticker}"
        cached_geo = cache_service.get(cache_key)
        if cached_geo:
            return cached_geo
            
        geo = YFinanceService.get_etf_geography(ticker)
        if geo:
            cache_service.set(cache_key, geo, ttl=604800)
            return geo
            
        return {}

    @staticmethod
    def search_tickers(query: str, limit: int = 10, asset_type: str = "etf"):
        """Search universe using financedatabase if available, else simple fallback"""
        # Basic caching for searches
        cache_key = f"search_{query}_{asset_type}_{limit}"
        cached_search = cache_service.get(cache_key)
        if cached_search:
            return cached_search
            
        results = []
        if fd_available and asset_type.lower() == "etf":
            try:
                # Get the ETF database
                etfs = fd.ETFs()
                # Search by name or symbol (financedatabase returns a DataFrame)
                # This is a bit slow so we only do a basic filter
                df = etfs.select()
                if not df.empty:
                    # Very simple rudimentary search implementation
                    mask = (df.index.str.contains(query.upper(), na=False)) | \
                           (df['name'].str.contains(query, case=False, na=False))
                    matches = df[mask].head(limit)
                    
                    for idx, row in matches.iterrows():
                        results.append({
                            "ticker": idx,
                            "name": row.get('name', 'Unknown'),
                            "category": row.get('category', 'Unknown'),
                            "family": row.get('family', 'Unknown')
                        })
            except Exception as e:
                print(f"FinanceDatabase search error: {e}")
                
        # If no results and it looks like a ticker, return just the ticker payload
        if not results and query.upper().isalpha() and len(query) <= 5:
             # Basic fallback payload
             results.append({
                 "ticker": query.upper(),
                 "name": f"{query.upper()} (via direct ticker)",
                 "category": "Unknown",
                 "family": "Unknown"
             })
             
        if results:
            cache_service.set(cache_key, results, ttl=86400) # 1 day cache
            
        return results
