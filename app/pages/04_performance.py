import streamlit as st
st.set_page_config(page_title="Mudric Lab — Portfolio Intelligence", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
from datetime import datetime, timedelta

from app.components.sidebar import sidebar_nav
from app.components.styles import inject_global_css
from app.components.metrics import section_header
from app.components.tables import data_table
from app.services.data_provider import DataProvider
from app.database.models import Holding

def format_large_number(num):
    if num is None:
        return "N/A"
    try:
        val = float(num)
        if val >= 1_000_000_000:
            return f"${val/1_000_000_000:.2f}B"
        elif val >= 1_000_000:
            return f"${val/1_000_000:.2f}M"
        return f"${val:,.0f}"
    except (ValueError, TypeError):
        return str(num)

def render_performance():
    section_header("Performance Analytics", "Advanced portfolio metrics and ETF comparison.")
    
    st.markdown("### ETF Comparison Tool")
    st.write("Compare key metrics, return profiles, and analyze holding overlaps.")
    
    from app.database.connection import SessionLocal
    db = SessionLocal()
    
    # Fetch all tickers across user portfolios in the active workspace
    ws_id = st.session_state.get("workspace_id", "default")
    portfolio_holdings = db.query(Holding.ticker).join(Portfolio).filter(Portfolio.workspace_id == ws_id).distinct().all()
    portfolio_tickers = [h[0] for h in portfolio_holdings]
    
    # Initialize session state for additional search tickers if not present
    if "comparison_tickers" not in st.session_state:
        st.session_state.comparison_tickers = portfolio_tickers if portfolio_tickers else ["VTI", "VXUS", "SPY"]

    col_comp_search, col_comp_add = st.columns([3, 1])
    
    with col_comp_add:
        new_ticker = st.text_input("Add Ticker", placeholder="e.g. NVDA, VOO").upper().strip()
        if st.button("Add to Compare", use_container_width=True):
            if new_ticker and new_ticker not in st.session_state.comparison_tickers:
                st.session_state.comparison_tickers.append(new_ticker)
                st.rerun()

    with col_comp_search:
        compare_tickers = st.multiselect(
            "Select ETFs to compare",
            options=st.session_state.comparison_tickers,
            default=st.session_state.comparison_tickers[:2] if len(st.session_state.comparison_tickers) >= 2 else st.session_state.comparison_tickers,
            max_selections=4
        )
    
    db.close()
    
    if compare_tickers:
        if len(compare_tickers) == 1:
            st.info("Select at least one more ETF to begin comparison.")
        else:
            with st.spinner("Analyzing cross-metrics..."):
                comp_data = []
                all_holdings = {}
                
                for t in compare_tickers:
                    prof = DataProvider.get_etf_profile(t)
                    hlds = DataProvider.get_etf_holdings(t)
                    prices = DataProvider.get_price_history(t, start=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"))
                    
                    # Calculate 1Y return
                    ret_1y = 0.0
                    if prices:  # prices is a dict, so just check if truthy
                        df_p = pd.DataFrame.from_dict(prices, orient='index')
                        if len(df_p) > 200: # rough check for 1 year of data
                            ret_1y = (df_p['Close'].iloc[-1] / df_p['Close'].iloc[0]) - 1

                    comp_data.append({
                        "Ticker": t,
                        "Name": prof.get("name", "N/A"),
                        "AUM": format_large_number(prof.get("aum")),
                        "Exp Ratio": f"{((prof.get('expense_ratio') or 0) * 100):.2f}%",
                        "1Y Return": f"{(ret_1y * 100):.2f}%",
                        "Category": prof.get("benchmark", "N/A")
                    })
                    
                    if hlds:
                        # Ensure we store floats, not strings
                        all_holdings[t] = {
                            h["symbol"]: float(h.get("holdingPercent", 0)) if pd.notnull(h.get("holdingPercent")) else 0.0 
                            for h in hlds
                        }
                
                # Render Comparison Table
                st.markdown("#### Key Metrics")
                df_comp = pd.DataFrame(comp_data).set_index("Ticker").T
                st.dataframe(df_comp, use_container_width=True)
                
                # Render Overlap Analysis (Top 10 basis)
                st.markdown("#### Holdings Overlap (Top 10)")
                if len(compare_tickers) == 2:
                    t1, t2 = compare_tickers[0], compare_tickers[1]
                    h1, h2 = all_holdings.get(t1, {}), all_holdings.get(t2, {})
                    
                    common_keys = set(h1.keys()).intersection(set(h2.keys()))
                    if common_keys:
                        overlap_data = []
                        for k in common_keys:
                            overlap_data.append({
                                "Symbol": k,
                                f"{t1} Weight": f"{(h1[k]*100):.2f}%",
                                f"{t2} Weight": f"{(h2[k]*100):.2f}%"
                            })
                        df_overlap = pd.DataFrame(overlap_data)
                        st.write(f"Found **{len(common_keys)}** overlapping assets in their Top 10 holdings.")
                        data_table(df_overlap, table_key=f"overlap_table_{t1}_{t2}")
                    else:
                        st.success(f"No overlap found between the Top 10 holdings of {t1} and {t2}.")
                else:
                    st.info("Holdings overlap analysis is currently optimized for 2 ETFs. Select exactly 2 ETFs to see overlap.")

if __name__ == "__main__":
    inject_global_css()
    sidebar_nav("Performance")
    render_performance()
