import streamlit as st
st.set_page_config(page_title="Mudric Lab — Portfolio Intelligence", layout="wide", initial_sidebar_state="expanded")

import os
from app.components.sidebar import sidebar_nav
from app.components.styles import inject_global_css
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
        av_key = st.text_input("AlphaVantage API Key (Community Access)", value=st.session_state.api_keys.get("ALPHA_VANTAGE_API_KEY", ""), type="password")
        
        st.markdown("---")
        st.info("Professional Data Tiers (Requires Mudric Pro License)")
        
        fmp_key = st.text_input("Financial Modeling Prep (FMP) API Key", value=st.session_state.api_keys.get("FMP_API_KEY", ""), type="password", disabled=True, help="Contact info@mudric.com for professional access")
        openbb_key = st.text_input("OpenBB API Key", value=st.session_state.api_keys.get("OPENBB_API_KEY", ""), type="password", disabled=True, help="Contact info@mudric.com for professional access")
        polygon_key = st.text_input("Massive.com (formerly Polygon.io) API Key", value=st.session_state.api_keys.get("POLYGON_API_KEY", ""), type="password", disabled=True, help="Contact info@mudric.com for professional access")
        
        st.markdown("""
            <div style="background-color: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 8px; border-left: 5px solid #3B82F6; margin-bottom: 20px;">
                <p style="margin: 0; color: #E8EAED; font-size: 0.9rem;">
                    <b>Professional Data streams are currently locked.</b><br>
                    To enable high-frequency data from FMP, OpenBB, and Massive.com, please reach out to our team at 
                    <a href="mailto:info@mudric.com" style="color: #00D4AA; text-decoration: none; font-weight: 600;">info@mudric.com</a>.
                </p>
            </div>
        """, unsafe_allow_html=True)

        submitted = st.form_submit_button("Save Settings")
        
        if submitted:
            st.session_state.api_keys = {
                "ALPHA_VANTAGE_API_KEY": av_key,
                "FMP_API_KEY": st.session_state.api_keys.get("FMP_API_KEY", ""), # Keep existing as it's disabled
                "OPENBB_API_KEY": st.session_state.api_keys.get("OPENBB_API_KEY", ""),
                "POLYGON_API_KEY": st.session_state.api_keys.get("POLYGON_API_KEY", "")
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
    inject_global_css()
    sidebar_nav("Settings")
    render_settings()
