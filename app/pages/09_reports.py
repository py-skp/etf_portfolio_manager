import streamlit as st
st.set_page_config(page_title="Mudric Lab — Portfolio Intelligence", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
from datetime import datetime, timedelta

from app.components.sidebar import sidebar_nav
from app.components.metrics import section_header, metric_card
from app.components.charts import plot_price_history, plot_allocation_donut, plot_var_histogram
from app.components.tables import data_table
from app.services.data_provider import DataProvider
from app.analytics.performance import PerformanceAnalytics

def inject_print_css():
    """CSS to hide Streamlit UI elements when 'Generate Tear Sheet' is active"""
    st.markdown("""
        <style>
            /* Hide Sidebar */
            [data-testid="stSidebar"] { display: none; }
            /* Hide top header */
            header { display: none; }
            /* Hide bottom footer */
            footer { display: none; }
            /* Hide the 'Deploy' button and multi-selects to make it clean */
            .stMultiSelect, .stSelectbox, .stTextInput, .stButton { display: none; }
            /* Force white background for printing (override dark mode if printing) */
            @media print {
                body, .stApp { background-color: white !important; color: black !important; }
                h1, h2, h3, h4, h5, h6, p, span { color: black !important; }
                /* But keep our custom containers looking okay */
            }
        </style>
    """, unsafe_allow_html=True)

def render_tear_sheet(ticker):
    """Renders a consolidated, un-tabbed view of an ETF for printing"""
    with st.spinner(f"Compiling Tear Sheet for {ticker}..."):
        profile = DataProvider.get_etf_profile(ticker)
        holdings = DataProvider.get_etf_holdings(ticker)
        sectors = DataProvider.get_etf_sectors(ticker)
        
        # Performance data
        start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y-%m-%d")
        prices = DataProvider.get_price_history(ticker, start=start_date)
        df_p = pd.DataFrame.from_dict(prices, orient='index') if prices else pd.DataFrame()
        
        bench_prices = DataProvider.get_price_history("SPY", start=start_date)
        df_b = pd.DataFrame.from_dict(bench_prices, orient='index') if bench_prices else pd.DataFrame()

    if not profile:
        st.error("ETF Profile not found.")
        return

    # Header
    st.markdown(f"## {profile.get('name', ticker)} ({ticker})")
    st.markdown(f"**Issuer:** {profile.get('issuer', 'N/A')} | **Category:** {profile.get('benchmark', 'N/A')} | **Date:** {datetime.now().strftime('%Y-%m-%d')}")
    st.divider()
    
    # Key Stats
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total AUM", f"${profile.get('aum', 0):,.0f}" if profile.get('aum') else "N/A")
    with c2:
        st.metric("Expense Ratio", f"{((profile.get('expense_ratio') or 0) * 100):.2f}%")
    with c3:
        st.metric("YTD Return", f"{((profile.get('ytd_return') or 0) * 100):.2f}%")
    with c4:
        st.metric("Yield", f"{((profile.get('yield') or 0) * 100):.2f}%" if profile.get('yield') else "N/A")

    st.markdown("---")
    
    # Body Row 1: Chart and Risk
    col_chart, col_risk = st.columns([2, 1])
    with col_chart:
        st.markdown("### 3-Year Growth ($10k)")
        if not df_p.empty:
            df_p.index = pd.to_datetime(df_p.index)
            returns = PerformanceAnalytics.calculate_returns(df_p)
            equity = (1 + returns).cumprod() * 10000
            
            equity_df = pd.DataFrame({ticker: equity})
            if not df_b.empty:
                df_b.index = pd.to_datetime(df_b.index)
                bench_returns = PerformanceAnalytics.calculate_returns(df_b)
                # Align dates
                common = returns.index.intersection(bench_returns.index)
                bench_eq = (1 + bench_returns.loc[common]).cumprod() * 10000
                equity_df["SPY"] = bench_eq
                
            fig_p = plot_price_history(equity_df, x_col=equity_df.index.name or "Date", y_cols=list(equity_df.columns), title="")
            st.plotly_chart(fig_p, use_container_width=True)
            
    with col_risk:
        st.markdown("### Risk Analytics")
        if not df_p.empty:
            vol = PerformanceAnalytics.get_annualized_volatility(returns)
            mdd = PerformanceAnalytics.get_max_drawdown(returns)
            var95 = PerformanceAnalytics.calculate_historical_var(returns, 0.95)
            
            st.metric("Ann. Volatility", f"{(vol*100):.1f}%")
            st.metric("Max Drawdown", f"{(mdd*100):.1f}%")
            st.metric("Daily VaR (95%)", f"{(var95*100):.2f}%")
            
            if not df_b.empty:
                beta = PerformanceAnalytics.calculate_beta(returns, bench_returns)
                st.metric("Beta (vs SPY)", f"{beta:.2f}")

    st.markdown("---")
    
    # Body Row 2: Holdings and Sectors
    col_h, col_s = st.columns(2)
    with col_h:
        st.markdown("### Top 10 Holdings")
        if holdings:
            df_h = pd.DataFrame(holdings)
            if 'holdingPercent' in df_h.columns:
                df_h['holdingPercent'] = pd.to_numeric(df_h['holdingPercent'], errors='coerce').fillna(0) * 100
                df_h.rename(columns={'symbol': 'Ticker', 'holdingName': 'Name', 'holdingPercent': 'Weight %'}, inplace=True)
                data_table(df_h.head(10), format_dict={"Weight %": "{:.2f}"})
    
    with col_s:
        st.markdown("### Sector Exposure")
        if sectors:
             df_s = pd.DataFrame.from_dict(sectors, orient='index', columns=['Weight %']).reset_index()
             df_s.rename(columns={'index': 'Sector'}, inplace=True)
             df_s['Weight %'] = pd.to_numeric(df_s['Weight %'], errors='coerce').fillna(0) * 100
             df_s = df_s.sort_values(by='Weight %', ascending=False).head(8)
             fig_s = plot_allocation_donut(df_s, 'Sector', 'Weight %', title="")
             st.plotly_chart(fig_s, use_container_width=True)
             
    st.caption("Generated by Mudric Lab Portfolio Intelligence. Not financial advice.")

def render_reports():
    
    # If we are in "Tear Sheet" mode, hijack the page render
    if st.session_state.get("tear_sheet_active", False):
        inject_print_css()
        # Render a button to go back (it will be hidden during actual print via CSS)
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        if st.button("← Back to Reports Dashboard"):
            st.session_state.tear_sheet_active = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<style>@media print { .no-print { display: none; } }</style>', unsafe_allow_html=True)
        
        render_tear_sheet(st.session_state.get("tear_sheet_ticker", "VTI"))
        return

    # Normal Dashboard Mode
    section_header("Reporting Engine", "Generate institutional tear sheets and PDF reports.")
    
    st.markdown("### Tear Sheet Generator")
    st.write("A tear sheet is a concise, one-page summary of an asset's key characteristics, designed for easy reading and printing.")
    
    st.info("💡 **Pro Tip**: After generating the tear sheet, simply press `Cmd + P` (or `Ctrl + P`) in your browser to save it as a PDF.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        target_ticker = st.text_input("Enter ETF Ticker", value="QQQ").upper()
    with col2:
        st.write("")
        st.write("")
        if st.button("Generate Tear Sheet", type="primary", use_container_width=True):
            st.session_state.tear_sheet_active = True
            st.session_state.tear_sheet_ticker = target_ticker
            st.rerun()

if __name__ == "__main__":
    sidebar_nav("Reports")
    render_reports()
