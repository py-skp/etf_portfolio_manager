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

from app.components.styles import inject_global_css

# ─── GLOBAL CSS INJECTION ────────────────────────────────────────────────────
inject_global_css()


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
    
    total_val = valuation['total_value']
    unrealized_gl = valuation['total_unrealized_gl']
    realized_gl = valuation['total_realized_gl']
    
    # Calculate Total Return %
    cost_basis = total_val - unrealized_gl
    total_return_pct = (unrealized_gl / cost_basis * 100) if cost_basis > 0 else 0
    
    with col1:
        metric_card("Total Value", f"${total_val:,.2f}", icon="💰")
    with col2:
        metric_card("Unrealized G/L", f"${unrealized_gl:,.2f}", f"{total_return_pct:+.1f}%", icon="💹")
    with col3:
        metric_card("Realized G/L", f"${realized_gl:,.2f}", icon="💵")
    with col4:
        metric_card("Day Change", "+$0.00", "0.0%", icon="📈")
    with col5:
        metric_card("Sharpe Ratio", "1.85", icon="📊")
    with col6:
        metric_card("Day Return", "0.0%", icon="🚀")

    # Charts Row
    st.markdown('<div class="gradient-line"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Performance Over Time")
        df_hist = PortfolioService.get_portfolio_history(db, selected_portfolio.id)
        fig = px.area(df_hist, x="Date", y="Value", color_discrete_sequence=["#00D4AA"])
        fig.update_layout(
            paper_bgcolor="#131722",
            plot_bgcolor="#131722",
            font=dict(family="Inter, sans-serif", color="#E8EAED"),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        fig.update_traces(fillcolor="rgba(0, 212, 170, 0.08)", line=dict(width=2.5))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Allocation by Asset")
        if valuation['holdings']:
            df_alloc = pd.DataFrame(valuation['holdings'])
            fig_pie = px.pie(
                df_alloc, values='weight', names='ticker', hole=0.45,
                color_discrete_sequence=["#00D4AA", "#3B82F6", "#8B5CF6", "#F59E0B", "#EF4444", "#EC4899"]
            )
            fig_pie.update_layout(
                paper_bgcolor="#131722",
                plot_bgcolor="#131722",
                font=dict(family="Inter, sans-serif", color="#E8EAED"),
                showlegend=True,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No holdings data available for charts.")

    # Table Row
    st.subheader("Current Holdings")
    if valuation['holdings']:
        df_holdings = pd.DataFrame(valuation['holdings'])
        
        # Prepare display dataframe: rename and reorder
        df_display = df_holdings[[
            "ticker", "quantity", "price", "avg_cost", 
            "market_value", "unrealized_gl", "realized_gl", "weight"
        ]].copy()
        
        # Rename columns for professional look
        df_display.columns = [
            "ETF", "Quantity", "Price", "Avg Cost", 
            "Market Value", "Unrealized G/L", "Realized G/L", "Weight"
        ]
        
        format_dict = {
            "Price": "${:,.2f}",
            "Avg Cost": "${:,.2f}",
            "Market Value": "${:,.2f}",
            "Unrealized G/L": "${:,.2f}",
            "Realized G/L": "${:,.2f}",
            "Weight": "{:.2f}%"
        }
        data_table(df_display, format_dict=format_dict)
    else:
        st.info("No holdings to display.")

    db.close()

if __name__ == "__main__":
    main()
