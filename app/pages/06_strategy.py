import streamlit as st
st.set_page_config(page_title="Mudric Lab — Portfolio Intelligence", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
from datetime import datetime, timedelta

from app.components.sidebar import sidebar_nav
from app.components.styles import inject_global_css
from app.components.metrics import section_header, metric_card
from app.components.charts import plot_price_history
from app.components.tables import data_table
from app.services.data_provider import DataProvider
from app.analytics.performance import PerformanceAnalytics

def render_strategy():
    section_header("Strategy Builder", "Construct custom portfolios and run historical backtests.")
    
    st.markdown("### Portfolio Allocation")
    st.write("Add ETFs and assign target weights. Total weight must equal 100%.")
    
    # Initialize session state for portfolio configuration
    if "strategy_assets" not in st.session_state:
        st.session_state.strategy_assets = [{"Ticker": "VTI", "Weight": 60.0}, {"Ticker": "BND", "Weight": 40.0}]

    # Interactive UI for adding/removing assets
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        new_ticker = st.text_input("Ticker to Add", key="new_strat_ticker").upper()
    with col2:
        new_weight = st.number_input("Weight (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key="new_strat_weight")
    with col3:
        st.write("")
        st.write("")
        if st.button("Add Asset", use_container_width=True):
            if new_ticker and not any(a["Ticker"] == new_ticker for a in st.session_state.strategy_assets):
                st.session_state.strategy_assets.append({"Ticker": new_ticker, "Weight": new_weight})
                st.rerun()

    # Display editable configuration
    st.markdown("#### Current Target Weights")
    
    updated_assets = []
    total_weight = 0.0
    
    # Build dynamic rows for existing assets
    for i, asset in enumerate(st.session_state.strategy_assets):
        c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
        with c1:
            st.write("")
            st.write(f"**{asset['Ticker']}**")
        with c2:
            # We don't fetch names to keep it fast, or we could. Let's keep it simple.
            st.write("")
            st.caption("Asset")
        with c3:
            w = st.number_input(f"Weight for {asset['Ticker']}", min_value=0.0, max_value=100.0, value=float(asset['Weight']), step=1.0, key=f"weight_{i}", label_visibility="collapsed")
            total_weight += w
        with c4:
            if st.button("Remove", key=f"remove_{i}", use_container_width=True):
                st.session_state.strategy_assets.pop(i)
                st.rerun()
                
        updated_assets.append({"Ticker": asset["Ticker"], "Weight": w})

    st.session_state.strategy_assets = updated_assets
    
    # Weight validation
    if abs(total_weight - 100.0) < 0.01:
        st.success(f"Total Weight: {total_weight:.1f}%")
        valid_portfolio = True
    else:
        st.warning(f"Total Weight: {total_weight:.1f}% — Must equal exactly 100%.")
        valid_portfolio = False

    st.divider()

    # Backtesting Engine
    st.markdown("### Historical Backtest")
    lookback_years = st.slider("Lookback Period (Years)", min_value=1, max_value=10, value=3)
    
    if st.button("Run Simulation", disabled=not valid_portfolio, type="primary"):
        with st.spinner("Fetching historical data and running synthetic backtest..."):
            start_date = (datetime.now() - timedelta(days=365 * lookback_years)).strftime("%Y-%m-%d")
            
            price_data = {}
            for asset in st.session_state.strategy_assets:
                prices = DataProvider.get_price_history(asset["Ticker"], start=start_date)
                if prices:
                    df = pd.DataFrame.from_dict(prices, orient='index')
                    df.index = pd.to_datetime(df.index)
                    price_data[asset["Ticker"]] = df['Close']
            
            if not price_data:
                st.error("Could not fetch price data for the selected assets.")
                return

            # Combine into a single prices DataFrame
            portfolio_prices = pd.DataFrame(price_data).dropna()
            
            if portfolio_prices.empty:
                st.error("No overlapping historical data found for these assets during the selected period.")
                return

            # Calculate daily returns for each asset
            asset_returns = portfolio_prices.pct_change().dropna()
            
            # Create a Series of weights aligned with the columns
            weights = pd.Series({a["Ticker"]: a["Weight"] / 100.0 for a in st.session_state.strategy_assets})
            weights = weights[asset_returns.columns] # Ensure alignment
            
            # Calculate daily portfolio return (dot product of asset returns and weights)
            portfolio_returns = asset_returns.dot(weights)
            
            # Calculate SPY benchmark if enough data
            bench_prices = DataProvider.get_price_history("SPY", start=start_date)
            bench_returns = pd.Series()
            if bench_prices:
                df_b = pd.DataFrame.from_dict(bench_prices, orient='index')
                df_b.index = pd.to_datetime(df_b.index)
                bench_returns = df_b['Close'].pct_change().dropna()
                # Align benchmark with portfolio dates
                common_dates = portfolio_returns.index.intersection(bench_returns.index)
                portfolio_returns = portfolio_returns.loc[common_dates]
                bench_returns = bench_returns.loc[common_dates]

            # Generate Equity Curve (Base 10,000)
            initial_capital = 10000
            port_equity = (1 + portfolio_returns).cumprod() * initial_capital
            
            equity_df = pd.DataFrame({"Strategy": port_equity})
            if not bench_returns.empty:
                bench_equity = (1 + bench_returns).cumprod() * initial_capital
                equity_df["SPY (Benchmark)"] = bench_equity

            # Plot Equity Curve
            fig = plot_price_history(equity_df, x_col=equity_df.index.name or "Date", y_cols=list(equity_df.columns), title="Hypothetical Growth of $10,000")
            st.plotly_chart(fig, use_container_width=True)

            # Analytics
            st.markdown("#### Performance Summary")
            c1, c2, c3, c4 = st.columns(4)
            
            ann_ret = PerformanceAnalytics.get_annualized_return(portfolio_returns)
            ann_vol = PerformanceAnalytics.get_annualized_volatility(portfolio_returns)
            sharpe = PerformanceAnalytics.get_sharpe_ratio(portfolio_returns)
            mdd = PerformanceAnalytics.get_max_drawdown(portfolio_returns)
            
            with c1:
                metric_card("Annualized Return", f"{(ann_ret*100):.2f}%")
            with c2:
                metric_card("Annualized Volatility", f"{(ann_vol*100):.2f}%", delta_color="inverse")
            with c3:
                metric_card("Sharpe Ratio", f"{sharpe:.2f}")
            with c4:
                metric_card("Max Drawdown", f"{(mdd*100):.2f}%", delta_color="inverse")

            # Deep Risk
            st.markdown("#### Risk & Distribution")
            r1, r2, r3 = st.columns(3)
            var_95 = PerformanceAnalytics.calculate_historical_var(portfolio_returns, 0.95)
            alpha = PerformanceAnalytics.calculate_alpha(portfolio_returns, bench_returns) if not bench_returns.empty else 0.0
            beta = PerformanceAnalytics.calculate_beta(portfolio_returns, bench_returns) if not bench_returns.empty else 1.0

            with r1:
                st.metric("Historical VaR (95%)", f"{(var_95*100):.2f}%")
            with r2:
                st.metric("Portfolio Beta", f"{beta:.2f}")
            with r3:
                st.metric("Jensen's Alpha", f"{(alpha*100):.2f}%")

if __name__ == "__main__":
    inject_global_css()
    sidebar_nav("Strategy")
    render_strategy()
