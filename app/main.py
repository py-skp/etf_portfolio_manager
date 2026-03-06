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

# ─── GLOBAL CSS INJECTION ────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ═══════ Google Font Import ═══════ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ═══════ Root Variables ═══════ */
    :root {
        --bg-primary: #0B0E14;
        --bg-secondary: #131722;
        --bg-card: rgba(19, 23, 34, 0.7);
        --bg-card-hover: rgba(19, 23, 34, 0.9);
        --accent: #00D4AA;
        --accent-glow: rgba(0, 212, 170, 0.15);
        --accent-secondary: #3B82F6;
        --text-primary: #E8EAED;
        --text-secondary: #9CA3AF;
        --text-muted: #6B7280;
        --positive: #00D4AA;
        --negative: #EF4444;
        --warning: #F59E0B;
        --border: rgba(255, 255, 255, 0.06);
        --border-hover: rgba(0, 212, 170, 0.3);
        --radius: 12px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ═══════ Global Resets ═══════ */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    /* ═══════ Scrollbar ═══════ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--text-muted); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

    /* ═══════ Sidebar ═══════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1117 0%, #131722 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-primary) !important;
    }

    /* ═══════ Main Content Area ═══════ */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }

    /* ═══════ Headers & Typography ═══════ */
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.5rem !important; color: var(--text-primary) !important; }
    h3 { font-size: 1.15rem !important; color: var(--text-secondary) !important; }

    /* ═══════ Streamlit Metric Boxes ═══════ */
    [data-testid="stMetricValue"] {
        color: var(--accent) !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricDelta"] svg { display: inline; }

    /* ═══════ Glassmorphic Cards ═══════ */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: var(--transition);
    }
    .glass-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-hover);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 212, 170, 0.08);
    }

    /* ═══════ Buttons ═══════ */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, #00B894 100%) !important;
        color: #0B0E14 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        transition: var(--transition) !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.02em !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(0, 212, 170, 0.3) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Secondary / Download buttons */
    .stDownloadButton > button {
        background: transparent !important;
        color: var(--accent) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--accent) !important;
        background: var(--accent-glow) !important;
    }

    /* ═══════ Inputs ═══════ */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        transition: var(--transition) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
    }

    /* ═══════ Tabs ═══════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: var(--bg-secondary);
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        padding: 8px 20px;
        transition: var(--transition);
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--accent) !important;
        color: #0B0E14 !important;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ═══════ Dataframes / Tables ═══════ */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden;
    }
    .stDataFrame thead tr th {
        background-color: var(--bg-secondary) !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em !important;
    }

    /* ═══════ Dividers ═══════ */
    hr {
        border-color: var(--border) !important;
        margin: 1.5rem 0 !important;
    }

    /* ═══════ Progress Bars ═══════ */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent) 0%, #00B894 100%) !important;
        border-radius: 10px !important;
    }

    /* ═══════ Alerts ═══════ */
    .stAlert {
        border-radius: var(--radius) !important;
        border: 1px solid var(--border) !important;
    }

    /* ═══════ Expander ═══════ */
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary) !important;
        border-radius: var(--radius) !important;
        font-weight: 500 !important;
    }

    /* ═══════ Slider ═══════ */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: var(--accent) !important;
    }

    /* ═══════ Spinner ═══════ */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }

    /* ═══════ Responsive ═══════ */
    @media (max-width: 768px) {
        .main .block-container { padding: 1rem 0.5rem !important; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        .glass-card { padding: 0.75rem; }
    }

    /* ═══════ Animated Gradient Accent Line ═══════ */
    .gradient-line {
        height: 3px;
        background: linear-gradient(90deg, var(--accent), var(--accent-secondary), var(--accent));
        background-size: 200% auto;
        animation: gradient-flow 3s ease infinite;
        border-radius: 2px;
        margin: 0.5rem 0 1.5rem 0;
    }
    @keyframes gradient-flow {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    /* ═══════ Fade In Animation ═══════ */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main .block-container > div {
        animation: fadeInUp 0.4s ease-out;
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
        metric_card("Day Change", "+$1,240", "+1.2%", icon="📈")
    with col3:
        metric_card("Total Return", "15.4%", "+15.4%", icon="🚀")
    with col4:
        metric_card("Sharpe Ratio", "1.85", icon="📊")
    with col5:
        metric_card("Max Drawdown", "-8.2%", icon="⚠️")
    with col6:
        metric_card("Dividend Yield", "2.1%", icon="💵")

    # Charts Row
    st.markdown('<div class="gradient-line"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Performance Over Time")
        df_hist = pd.DataFrame({
            "Date": pd.date_range(start="2023-01-01", periods=12, freq="M"),
            "Value": [100000, 102000, 101500, 105000, 108000, 110000, 112000, 115000, 114000, 118000, 122000, 124500]
        })
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
        data_table(df_holdings)
    else:
        st.info("No holdings to display.")

    db.close()

if __name__ == "__main__":
    main()
