import streamlit as st
st.set_page_config(page_title="Mudric Lab — Portfolio Intelligence", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
from datetime import datetime, timedelta

from app.components.sidebar import sidebar_nav
from app.components.metrics import section_header, metric_card
from app.components.tables import data_table
from app.components.charts import plot_price_history, plot_allocation_donut, plot_horizontal_bar, plot_choropleth
from app.services.data_provider import DataProvider
from app.analytics.performance import PerformanceAnalytics

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

def render_etf_intelligence():
    section_header("ETF Intelligence", "Institutional research and deep analytics.")
    
    # 1. Top Section: Search & Quick Stats
    st.markdown("### Search Universe")
    
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        search_query = st.text_input("Enter Ticker or Name (e.g., VTI, Vanguard)", value="VTI")
    with col_btn:
        st.write("") # Spacing
        st.write("")
        search_pressed = st.button("Search", use_container_width=True)

    if search_query:
        # Resolve ticker if name was entered
        search_results = DataProvider.search_tickers(search_query)
        if search_results:
             selected_ticker = search_results[0]["ticker"].upper()
             # If multiple and not exact match, optionally show a selectbox
             if len(search_results) > 1 and search_query.upper() != selected_ticker:
                 selected_ticker = st.selectbox(
                     "Multiple matches found. Select one:", 
                     options=[r["ticker"] for r in search_results],
                     format_func=lambda x: next(r["name"] for r in search_results if r["ticker"]==x) + f" ({x})"
                 )
        else:
             selected_ticker = search_query.upper()

        st.divider()

        with st.spinner(f"Fetching profile for {selected_ticker}..."):
            profile = DataProvider.get_etf_profile(selected_ticker)
            prices = DataProvider.get_price_history(selected_ticker, start=(datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d"))
        
        if not profile or not profile.get("name"):
            st.error(f"Could not retrieve profile data for '{selected_ticker}'. Please verify the ticker symbol.")
            return

        # Profile Header Card
        st.markdown(f"""
        <div style="
            background: rgba(19, 23, 34, 0.6);
            backdrop-filter: blur(12px);
            padding: 24px;
            border-radius: 12px;
            border-left: 4px solid #00D4AA;
            border: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 20px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h2 style="margin: 0; color: #E8EAED; font-weight: 700;">{profile.get('name', 'N/A')} ({selected_ticker})</h2>
                    <p style="color: #9CA3AF; margin: 5px 0;">{profile.get('issuer', 'Unknown Issuer')} | {profile.get('asset_class', 'Unknown Class')} | {profile.get('exchange', 'Unknown Exchange')}</p>
                </div>
                <div style="text-align: right;">
                    <h3 style="margin: 0; color: #E8EAED;">{DataProvider.get_current_price(selected_ticker) or 'N/A'} {profile.get('currency', 'USD')}</h3>
                    <p style="color: {'#00D4AA' if (profile.get('ytd_return') or 0) > 0 else '#EF4444'}; margin: 5px 0;">
                        YTD: {((profile.get('ytd_return') or 0) * 100):.2f}%
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 30px; margin-top: 15px; border-top: 1px solid #262730; padding-top: 15px;">
                <div><span style="color: #94A3B8;">AUM:</span> {format_large_number(profile.get('aum'))}</div>
                <div><span style="color: #94A3B8;">Exp Ratio:</span> {((profile.get('expense_ratio') or 0) * 100):.2f}%</div>
                <div><span style="color: #94A3B8;">Inception:</span> {str(profile.get('inception_date', 'N/A'))[:10]}</div>
                <div><span style="color: #94A3B8;">Benchmark:</span> {profile.get('benchmark', 'N/A')}</div>
            </div>
            <div style="display: flex; gap: 30px; margin-top: 10px;">
                <div><span style="color: #94A3B8;">52W Range:</span> {profile.get('fifty_two_week_low', 'N/A')} - {profile.get('fifty_two_week_high', 'N/A')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tabs
        tab_hold, tab_sec, tab_geo, tab_perf, tab_ana, tab_analyst = st.tabs([
            "Holdings", "Sector Exposure", "Geographic Exposure", "Performance", "Analytics", "Analyst View"
        ])

        with tab_hold:
            st.markdown("### Top 10 Holdings")
            with st.spinner("Loading holdings data..."):
                holdings = DataProvider.get_etf_holdings(selected_ticker)
                if holdings:
                    df_h = pd.DataFrame(holdings)
                    # Force numeric conversion on the source column first
                    if 'holdingPercent' in df_h.columns:
                        df_h['holdingPercent'] = pd.to_numeric(df_h['holdingPercent'], errors='coerce').fillna(0)
                    
                    df_h.rename(columns={'symbol': 'Ticker', 'holdingName': 'Name', 'holdingPercent': 'Weight %'}, inplace=True)
                    df_h['Weight %'] = df_h['Weight %'].astype(float) * 100
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        data_table(df_h, format_dict={"Weight %": "{:.2f}"})
                    with c2:
                        top_5 = df_h.head(5).copy()
                        total_top_weight = float(top_5['Weight %'].sum())
                        other_pct = max(0.0, 100.0 - total_top_weight)
                        
                        # Add 'OTHER' row
                        new_row = pd.DataFrame({
                            'Ticker': ['OTHER'], 
                            'Name': ['All Others'], 
                            'Weight %': [other_pct]
                        })
                        top_5 = pd.concat([top_5, new_row], ignore_index=True)
                        
                        fig = plot_allocation_donut(top_5, 'Ticker', 'Weight %', "")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Holdings data not available for this ticker.")

        with tab_sec:
            st.markdown("### Sector Breakdown")
            with st.spinner("Loading sector data..."):
                sectors = DataProvider.get_etf_sectors(selected_ticker)
                if sectors:
                    df_s = pd.DataFrame(list(sectors.items()), columns=['Sector', 'Weight %'])
                    df_s['Weight %'] = pd.to_numeric(df_s['Weight %'], errors='coerce').fillna(0) * 100
                    df_s = df_s.sort_values('Weight %', ascending=True) # Ascending for horizontal bar
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                         fig = plot_horizontal_bar(df_s, x_col='Weight %', y_col='Sector', title="")
                         st.plotly_chart(fig, use_container_width=True)
                    with c2:
                         data_table(df_s.sort_values('Weight %', ascending=False), format_dict={"Weight %": "{:.2f}"})
                else:
                    st.info("Sector data not available.")

        with tab_geo:
            st.markdown("### Geographic Exposure")
            with st.spinner("Loading geographic data..."):
                geo = DataProvider.get_etf_geography(selected_ticker)
                if geo:
                    df_g = pd.DataFrame(list(geo.items()), columns=['Region', 'Weight %'])
                    df_g['Weight %'] = pd.to_numeric(df_g['Weight %'], errors='coerce').fillna(0) * 100
                    
                    fig = plot_choropleth(df_g, 'Region', 'Weight %', title="")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    data_table(df_g.sort_values('Weight %', ascending=False), format_dict={"Weight %": "{:.2f}"})
                else:
                    st.info("Geographic exposure data not provided by main data source.")

        with tab_perf:
            st.markdown("### Historical Performance")
            if prices:
                df_p = pd.DataFrame.from_dict(prices, orient='index')
                df_p.index = pd.to_datetime(df_p.index)
                
                # Check for benchmark to overlay
                bench_ticker = profile.get("benchmark")
                if bench_ticker and bench_ticker != "N/A":
                    # Simple heuristic: SPY as default equity benchmark
                    bench_prices = DataProvider.get_price_history("SPY", start=(datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d"))
                    if bench_prices:
                        df_b = pd.DataFrame.from_dict(bench_prices, orient='index')
                        df_b.index = pd.to_datetime(df_b.index)
                        
                        # Normalize to 100 for comparison
                        df_merged = pd.DataFrame()
                        df_merged['Asset'] = df_p['Close'] / df_p['Close'].iloc[0] * 100
                        df_merged['SPY (Bench)'] = df_b['Close'] / df_b['Close'].iloc[0] * 100
                        
                        fig = plot_price_history(df_merged.reset_index(), x_col='index', y_cols=['Asset', 'SPY (Bench)'], title="Normalized Growth (100 Base)")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = plot_price_history(df_p.reset_index(), x_col='index', y_cols=['Close'], title="Price History")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Price history not available.")

        with tab_ana:
            st.markdown("### Risk & Return Analytics (5Y)")
            if prices:
                df_p = pd.DataFrame.from_dict(prices, orient='index')
                rets = PerformanceAnalytics.calculate_returns(df_p)
                
                col1, col2, col3 = st.columns(3)
                
                ann_ret = PerformanceAnalytics.get_annualized_return(rets)
                ann_vol = PerformanceAnalytics.get_annualized_volatility(rets)
                sharpe = PerformanceAnalytics.get_sharpe_ratio(rets)
                mdd = PerformanceAnalytics.get_max_drawdown(rets)
                
                with col1:
                    metric_card("Annualized Return", f"{(ann_ret*100):.2f}%")
                    metric_card("Annualized Volatility", f"{(ann_vol*100):.2f}%")
                with col2:
                    metric_card("Sharpe Ratio", f"{sharpe:.2f}")
                    metric_card("Max Drawdown", f"{(mdd*100):.2f}%", delta_color="inverse")
                with col3:
                     # Beta/Alpha vs SPY
                     raw_bench = DataProvider.get_price_history("SPY", start=(datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d"))
                     bench_prices = pd.DataFrame.from_dict(raw_bench, orient='index') if raw_bench else pd.DataFrame()
                     if not bench_prices.empty:
                         b_rets = PerformanceAnalytics.calculate_returns(bench_prices)
                         beta = PerformanceAnalytics.calculate_beta(rets, b_rets)
                         alpha = PerformanceAnalytics.calculate_alpha(rets, b_rets)
                         metric_card("Beta (vs SPY)", f"{beta:.2f}")
                         metric_card("Alpha (Ann.)", f"{(alpha*100):.2f}%")
            else:
                st.info("Analytics require price history.")

        with tab_analyst:
             st.markdown("### Analyst Consensus")
             
             # Check for keys in session state or environment
             import os
             api_keys = st.session_state.get("api_keys", {})
             av_key = api_keys.get("ALPHA_VANTAGE_API_KEY") or os.environ.get("ALPHA_VANTAGE_API_KEY")
             fmp_key = api_keys.get("FMP_API_KEY") or os.environ.get("FMP_API_KEY")
             
             if not av_key and not fmp_key:
                 st.info("Premium analyst data (Financial Modeling Prep / Alpha Vantage) is currently not configured.")
                 st.markdown("""
                 > Please add your API keys directly in the **Settings module** to enable premium fundamental data streams including:
                 > - Consensus Buy/Hold/Sell ratings
                 > - Price targets
                 > - Factor Analysis
                 """)
             else:
                 st.success("Premium API keys detected!")
                 
                 if av_key:
                     st.markdown("#### Real-Time Alpha Vantage Quote")
                     import requests
                     with st.spinner("Fetching live premium data..."):
                         try:
                             url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={selected_ticker}&apikey={av_key}"
                             response = requests.get(url)
                             data = response.json()
                             
                             if "Global Quote" in data and data["Global Quote"]:
                                 quote = data["Global Quote"]
                                 
                                 c1, c2, c3 = st.columns(3)
                                 with c1:
                                     metric_card("Live Price", f"${float(quote.get('05. price', 0)):.2f}")
                                 with c2:
                                     metric_card("Trading Volume", f"{int(quote.get('06. volume', 0)):,}")
                                 with c3:
                                     metric_card("Latest Trading Day", quote.get('07. latest trading day', 'N/A'))
                                     
                                 st.markdown("---")
                                 st.markdown(f"**Previous Close:** ${float(quote.get('08. previous close', 0)):.2f} | **Change:** {quote.get('10. change percent', 'N/A')}")
                             elif "Information" in data:
                                 st.warning(f"Alpha Vantage limit reached or endpoint restricted: {data['Information']}")
                             else:
                                 st.warning("No premium overview data available for this specific ticker on Alpha Vantage.")
                         except Exception as e:
                             st.error(f"Error fetching data from Alpha Vantage: {str(e)}")
                 else:
                     st.info("FMP key detected. Integration for FMP analyst targets coming soon.")

    # The ETF Comparison tool has been moved to the Performance page
if __name__ == "__main__":
    from app.components.sidebar import sidebar_nav
    sidebar_nav("ETF Intelligence")
    render_etf_intelligence()
