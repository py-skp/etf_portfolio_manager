import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from app.components.sidebar import sidebar_nav
from app.components.metrics import section_header, metric_card
from app.components.charts import plot_drawdown_chart, plot_var_histogram, plot_monte_carlo
from app.services.data_provider import DataProvider
from app.analytics.performance import PerformanceAnalytics

def render_risk():
    section_header("Risk Management", "Institutional risk analysis and forecasting.")
    
    st.markdown("### Select Asset")
    
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        search_query = st.text_input("Enter Ticker (e.g., SPY, QQQ)", value="SPY")
    with col_btn:
        st.write("")
        st.write("")
        search_pressed = st.button("Analyze Risk", use_container_width=True)

    if search_query:
        selected_ticker = search_query.upper()
        
        with st.spinner(f"Running risk engine for {selected_ticker}..."):
            # Fetch 5 years of daily data for robust risk modeling
            prices = DataProvider.get_price_history(selected_ticker, start=(datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d"))
            
            if not prices or len(prices) < 252:
                st.error("Insufficient price history available for robust risk analysis (minimum 1 year required).")
                return
                
            df_p = pd.DataFrame.from_dict(prices, orient='index')
            df_p.index = pd.to_datetime(df_p.index)
            returns = PerformanceAnalytics.calculate_returns(df_p)
            
            # Fetch Benchmark (SPY)
            bench_prices = DataProvider.get_price_history("SPY", start=(datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d"))
            df_b = pd.DataFrame.from_dict(bench_prices, orient='index') if bench_prices else pd.DataFrame()
            if not df_b.empty:
                df_b.index = pd.to_datetime(df_b.index)
                bench_returns = PerformanceAnalytics.calculate_returns(df_b)
            else:
                bench_returns = pd.Series()

        st.divider()

        tab_hist, tab_tail, tab_mc = st.tabs([
            "Historical Risk", "Tail Risk (VaR)", "Monte Carlo Simulation"
        ])

        with tab_hist:
            st.markdown("### Volatility & Drawdowns")
            
            col1, col2, col3 = st.columns(3)
            
            ann_vol = PerformanceAnalytics.get_annualized_volatility(returns)
            mdd = PerformanceAnalytics.get_max_drawdown(returns)
            beta = PerformanceAnalytics.calculate_beta(returns, bench_returns) if not bench_returns.empty else 1.0
            
            with col1:
                metric_card("Annualized Volatility (5Y)", f"{(ann_vol*100):.2f}%", delta_color="inverse")
            with col2:
                metric_card("Maximum Drawdown", f"{(mdd*100):.2f}%", delta_color="inverse")
            with col3:
                metric_card("Beta vs SPY", f"{beta:.2f}")
                
            st.write("")
            
            # Calculate rolling drawdown series
            cum_returns = (1 + returns).cumprod()
            rolling_max = cum_returns.cummax()
            drawdown_series = cum_returns / rolling_max - 1
            
            fig_dd = plot_drawdown_chart(drawdown_series, title=f"{selected_ticker} Historical Drawdown")
            st.plotly_chart(fig_dd, use_container_width=True)
            
            st.markdown("### Market Capture")
            if not bench_returns.empty:
                capture = PerformanceAnalytics.calculate_capture_ratios(returns, bench_returns)
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Up-Market Capture Ratio", f"{(capture['up_capture']*100):.1f}%", help="Performance relative to benchmark during positive benchmark months. >100% means outperformance.")
                with c2:
                    st.metric("Down-Market Capture Ratio", f"{(capture['down_capture']*100):.1f}%", delta_color="inverse", help="Performance relative to benchmark during negative benchmark months. <100% means less downside participation.")
            else:
                st.info("Market capture requires benchmark (SPY) data.")

        with tab_tail:
            st.markdown("### Tail Risk Analysis")
            st.write("Distribution of daily returns and extreme loss thresholds.")
            
            var_95 = PerformanceAnalytics.calculate_historical_var(returns, 0.95)
            cvar_95 = PerformanceAnalytics.calculate_cvar(returns, 0.95)
            var_99 = PerformanceAnalytics.calculate_historical_var(returns, 0.99)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                metric_card("Value at Risk (95%)", f"{(var_95*100):.2f}%", delta_color="inverse", subtitle="Daily loss threshold")
            with col2:
                metric_card("Expected Shortfall (CVaR 95%)", f"{(cvar_95*100):.2f}%", delta_color="inverse", subtitle="Avg loss beyond VaR")
            with col3:
                metric_card("Value at Risk (99%)", f"{(var_99*100):.2f}%", delta_color="inverse", subtitle="1-in-100 day event")
                
            fig_hist = plot_var_histogram(returns, var_95, cvar_95, title=f"{selected_ticker} Daily Return Distribution")
            st.plotly_chart(fig_hist, use_container_width=True)

        with tab_mc:
            st.markdown("### Forward-Looking Monte Carlo")
            st.write("10,000 simulated paths based on historical geometric brownian motion over the next 252 trading days.")
            
            with st.spinner("Running 10,000 simulations..."):
                ann_ret = PerformanceAnalytics.get_annualized_return(returns)
                current_price = df_p['Close'].iloc[-1]
                
                # Run MC
                mc_df = PerformanceAnalytics.run_monte_carlo_simulation(
                    initial_value=current_price,
                    mu=ann_ret,
                    sigma=ann_vol,
                    days=252,
                    simulations=10000,
                    seed=42
                )
                
            fig_mc = plot_monte_carlo(mc_df, title=f"1-Year Price Projections: {selected_ticker}")
            st.plotly_chart(fig_mc, use_container_width=True)
            
            st.markdown("#### Probability Matrix (1-Year Forward)")
            final_prices = mc_df.iloc[-1]
            prob_positive = (final_prices > current_price).mean() * 100
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", f"${current_price:.2f}")
            col2.metric("Median Target (50%)", f"${final_prices.median():.2f}")
            col3.metric("Bull Target (95%)", f"${final_prices.quantile(0.95):.2f}")
            col4.metric("Bear Target (5%)", f"${final_prices.quantile(0.05):.2f}")
            
            st.progress(prob_positive / 100.0)
            st.caption(f"**{prob_positive:.1f}%** probability of a positive return over the next year based on historical parameters.")

if __name__ == "__main__":
    sidebar_nav("Risk")
    render_risk()
