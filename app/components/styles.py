import streamlit as st

def inject_global_css():
    """Inject the Mudric Lab global CSS into any page that calls it."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #0B0E14;
        --bg-secondary: #131722;
        --bg-card: rgba(19, 23, 34, 0.7);
        --accent: #00D4AA;
        --accent-glow: rgba(0, 212, 170, 0.15);
        --accent-secondary: #3B82F6;
        --text-primary: #E8EAED;
        --text-secondary: #9CA3AF;
        --text-muted: #6B7280;
        --positive: #00D4AA;
        --negative: #EF4444;
        --border: rgba(255, 255, 255, 0.06);
        --border-hover: rgba(0, 212, 170, 0.3);
        --radius: 12px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    html, body, .stApp, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--text-muted); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1117 0%, #131722 100%) !important;
        border-right: 1px solid var(--border) !important;
    }

    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.5rem !important; color: var(--text-primary) !important; }
    h3 { font-size: 1.15rem !important; color: var(--text-secondary) !important; }

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

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        transition: var(--transition) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
    }

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
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden;
    }

    hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent) 0%, #00B894 100%) !important;
        border-radius: 10px !important;
    }

    .stAlert { border-radius: var(--radius) !important; }

    @keyframes gradient-flow {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main .block-container > div { animation: fadeInUp 0.4s ease-out; }

    @media (max-width: 768px) {
        .main .block-container { padding: 1rem 0.5rem !important; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)
