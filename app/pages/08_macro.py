import streamlit as st
st.set_page_config(page_title="Mudric Lab — Portfolio Intelligence", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.components.sidebar import sidebar_nav
from app.components.metrics import section_header, metric_card
from app.components.charts import apply_theme, THEME
from app.services.data_provider import DataProvider
from app.analytics.performance import PerformanceAnalytics

def fetch_yield_curve():
    """Fetch Treasury yields for the yield curve"""
    # 13W, 5Y, 10Y, 30Y Treasury Indexes
    tickers = {"13W": "^IRX", "5Y": "^FVX", "10Y": "^TNX", "30Y": "^TYX"}
    current_yields = {}
    past_yields = {} # 1 month ago
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=45) # Give buffer for weekends
    
    for label, ticker in tickers.items():
        data = DataProvider.get_price_history(ticker, start=start_date.strftime('%Y-%m-%d'))
        if data:
            df = pd.DataFrame.from_dict(data, orient='index')
            if not df.empty and 'Close' in df.columns:
                current_yields[label] = df['Close'].iloc[-1]
                # Find closest to 30 days ago
                past_target = end_date - timedelta(days=30)
                try:
                    past_idx = df.index.get_indexer([past_target], method='nearest')[0]
                    past_yields[label] = df['Close'].iloc[past_idx]
                except:
                    past_yields[label] = None
                    
    return current_yields, past_yields

def plot_yield_curve(current, past):
    """Plotly explicit line chart for the yield curve"""
    fig = go.Figure()
    
    x_labels = list(current.keys())
    y_current = list(current.values())
    y_past = [past.get(k) for k in x_labels]
    
    fig.add_trace(go.Scatter(
        x=x_labels, y=y_current,
        mode='lines+markers',
        name='Current Yields',
        line=dict(color=THEME["primary"], width=3),
        marker=dict(size=8)
    ))
    
    if any(y is not None for y in y_past):
        fig.add_trace(go.Scatter(
            x=x_labels, y=y_past,
            mode='lines+markers',
            name='1 Month Ago',
            line=dict(color=THEME["text"], width=2, dash='dot'),
            marker=dict(size=6)
        ))
        
    fig.update_layout(
        title="U.S. Treasury Yield Curve",
        yaxis_title="Yield (%)",
        xaxis_title="Maturity"
    )
    return apply_theme(fig)

def render_macro_dashboard():
    section_header("Macro Environment", "Top-down view of global markets, rates, and commodities.")
    
    st.markdown("### Interest Rates")
    
    with st.spinner("Loading Treasury yields..."):
        current_yields, past_yields = fetch_yield_curve()
        
    if current_yields:
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 3])
        
        # Safe extraction
        y_13w = current_yields.get("13W", 0)
        y_10y = current_yields.get("10Y", 0)
        p_10y = past_yields.get("10Y", 0)
        
        delta_10y = f"{(y_10y - p_10y):.2f} bps" if p_10y else "N/A"
        spread = y_10y - y_13w
        
        with c1:
            metric_card("13-Week T-Bill", f"{y_13w:.2f}%", subtitle="Short End")
        with c2:
            metric_card("10-Year T-Note", f"{y_10y:.2f}%", delta=delta_10y, subtitle="1Mo Δ")
        with c3:
            s_color = "normal" if spread > 0 else "inverse"
            s_label = "Normal" if spread > 0 else "Inverted"
            metric_card("10Y-3M Spread", f"{spread:.2f} bps", delta=s_label, delta_color=s_color, subtitle="Curve Shape")
            
        with c5:
            fig_yc = plot_yield_curve(current_yields, past_yields)
            st.plotly_chart(fig_yc, use_container_width=True)
            
    st.divider()
    
    st.markdown("### Broad Markets & Commodities")
    
    # Define macro trackers
    trackers = {
        "S&P 500 (SPY)": "SPY",
        "Nasdaq 100 (QQQ)": "QQQ",
        "Russell 2000 (IWM)": "IWM",
        "Gold (GLD)": "GLD",
        "Crude Oil (USO)": "USO",
        "US Dollar Index (UUP)": "UUP"
    }
    
    with st.spinner("Loading key indices..."):
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        cols = st.columns(3)
        i = 0
        for name, ticker in trackers.items():
            prices_dict = DataProvider.get_price_history(ticker, start=start_date)
            if prices_dict:
                df = pd.DataFrame.from_dict(prices_dict, orient='index')
                if not df.empty and len(df) > 20:
                    current_price = df['Close'].iloc[-1]
                    price_1mo = df['Close'].iloc[-21] # approx 1 trading month
                    price_ytd = df['Close'].iloc[0] # Very rough 1 year proxy here
                    
                    ret_1mo = (current_price / price_1mo) - 1
                    ret_1yr = (current_price / price_ytd) - 1
                    
                    with cols[i % 3]:
                        metric_card(
                            name, 
                            f"${current_price:.2f}", 
                            delta=f"1M: {(ret_1mo*100):.2f}% | 1Y: {(ret_1yr*100):.2f}%",
                            subtitle="Current Price"
                        )
                    i += 1

if __name__ == "__main__":
    sidebar_nav("Macro")
    render_macro_dashboard()
