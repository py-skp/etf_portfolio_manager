import streamlit as st
import pandas as pd
from app.components.sidebar import sidebar_nav
from app.components.metrics import metric_card, section_header
from app.components.tables import data_table
from app.database.connection import SessionLocal
from app.services.portfolio_service import PortfolioService
from app.services.data_provider import DataProvider
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Mudric Lab — Portfolio Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark theme adjustments
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        color: #D4A017 !important;
    }
    .stApp {
        background-color: #0F1117;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar Navigation
    selected_page = sidebar_nav("Dashboard")
    
    # Page Routing
    if selected_page == "Dashboard":
        render_dashboard()
    else:
        st.info(f"The {selected_page} page is coming soon in the next development phase!")

def render_dashboard():
    section_header("Executive Portfolio Dashboard", "Real-time institutional-grade analytics.")
    
    db = SessionLocal()
    portfolios = PortfolioService.get_portfolios(db)
    
    if not portfolios:
        st.warning("No portfolios found. Please go to the 'Portfolio' page to create one or run the seed script.")
        return

    # Select Portfolio
    selected_portfolio = st.selectbox("Select Portfolio", options=portfolios, format_func=lambda x: x.name)
    
    # Get Valuation
    valuation = PortfolioService.get_portfolio_valuation(db, selected_portfolio.id)
    
    # KPI Row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        metric_card("Total Value", f"${valuation['total_value']:,.2f}", "+2.4%", icon="💰")
    with col2:
        metric_card("Day Change", "+$1,240", "+1.2%", icon="📉")
    with col3:
        metric_card("Total Return", "15.4%", "+15.4%", icon="🚀")
    with col4:
        metric_card("Sharpe Ratio", "1.85", icon="📊")
    with col5:
        metric_card("Max Drawdown", "-8.2%", icon="⚠️")
    with col6:
        metric_card("Dividend Yield", "2.1%", icon="💵")

    # Charts Row
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Performance Over Time")
        # Placeholder for real historical data
        df_hist = pd.DataFrame({
            "Date": pd.date_range(start="2023-01-01", periods=12, freq="M"),
            "Value": [100000, 102000, 101500, 105000, 108000, 110000, 112000, 115000, 114000, 118000, 122000, 124500]
        })
        fig = px.area(df_hist, x="Date", y="Value", color_discrete_sequence=["#D4A017"])
        fig.update_layout(
            paper_bgcolor="#1A1A2E",
            plot_bgcolor="#1A1A2E",
            font_color="#F3F4F6",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#262730"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Allocation by Asset")
        if valuation['holdings']:
            df_alloc = pd.DataFrame(valuation['holdings'])
            fig_pie = px.pie(df_alloc, values='weight', names='ticker', hole=0.4, color_discrete_sequence=px.colors.sequential.YlOrBr)
            fig_pie.update_layout(
                paper_bgcolor="#1A1A2E",
                plot_bgcolor="#1A1A2E",
                font_color="#F3F4F6",
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No holdings data available for charts.")

    # Table Row
    st.subheader("Current Holdings")
    if valuation['holdings']:
        df_holdings = pd.DataFrame(valuation['holdings'])
        data_table(df_holdings)
    else:
        st.info("No holdings to display.")

    db.close()

if __name__ == "__main__":
    main()
