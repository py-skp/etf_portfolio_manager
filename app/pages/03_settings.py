import streamlit as st
import os
from app.components.sidebar import sidebar_nav
from app.components.metrics import section_header

def render_settings():
    section_header("Settings", "Manage your API keys and application preferences.")
    
    st.markdown("### API Configuration")
    st.write("Enter your API keys below. These will be stored in your browser session for this POC and will override any keys set in the environment.")
    
    # helper for safe secret access
    def get_init_key(name):
        try:
            # Try secrets first, then env
            return st.secrets.get(name, os.environ.get(name, ""))
        except:
            # Fallback to env if secrets system fails
            return os.environ.get(name, "")

    # Initialize session state for keys if not present
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {
            "ALPHA_VANTAGE_API_KEY": get_init_key("ALPHA_VANTAGE_API_KEY"),
            "FMP_API_KEY": get_init_key("FMP_API_KEY"),
            "OPENBB_API_KEY": get_init_key("OPENBB_API_KEY"),
            "POLYGON_API_KEY": get_init_key("POLYGON_API_KEY")
        }

    with st.form("settings_form"):
        av_key = st.text_input("AlphaVantage API Key", value=st.session_state.api_keys.get("ALPHA_VANTAGE_API_KEY", ""), type="password")
        fmp_key = st.text_input("Financial Modeling Prep (FMP) API Key", value=st.session_state.api_keys.get("FMP_API_KEY", ""), type="password")
        openbb_key = st.text_input("OpenBB API Key", value=st.session_state.api_keys.get("OPENBB_API_KEY", ""), type="password")
        polygon_key = st.text_input("Polygon.io API Key", value=st.session_state.api_keys.get("POLYGON_API_KEY", ""), type="password")
        
        submitted = st.form_submit_button("Save Settings")
        
        if submitted:
            st.session_state.api_keys = {
                "ALPHA_VANTAGE_API_KEY": av_key,
                "FMP_API_KEY": fmp_key,
                "OPENBB_API_KEY": openbb_key,
                "POLYGON_API_KEY": polygon_key
            }
            st.success("Settings saved successfully!")
            st.balloons()

    st.markdown("---")
    st.markdown("### Application Information")
    st.info("Mudric Lab — Portfolio Intelligence Platform (POC Phase 2.5)")
    st.write("**Version:** 0.2.5")
    st.write("**Data Providers:** yfinance, financedatabase (Primary)")
    st.write("**Storage:** PostgreSQL + Redis (Local)")

if __name__ == "__main__":
    sidebar_nav("Settings")
    render_settings()
