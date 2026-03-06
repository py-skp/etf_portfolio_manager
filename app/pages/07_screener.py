import streamlit as st
import pandas as pd

from app.components.sidebar import sidebar_nav
from app.components.metrics import section_header
from app.services.data_provider import DataProvider

def render_screener():
    section_header("ETF Screener", "Filter and discover exchange-traded funds matching your criteria.")
    
    with st.spinner("Loading global ETF universe..."):
        df = DataProvider.get_etf_universe()
        
    if df.empty:
        st.error("ETF database is currently unavailable. Please verify the `financedatabase` installation or your network connection.")
        return
        
    # Sidebar style filters inside an expander or columns
    st.markdown("### Search Filters")
    
    # We must ensure columns exist before filtering
    available_cols = df.columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Issuer / Family Filter
        if 'Issuer' in available_cols:
             issuers = ["All"] + sorted([str(x) for x in df['Issuer'].dropna().unique() if x != "N/A"])
             selected_issuer = st.selectbox("Fund Issuer", options=issuers)
        else:
             selected_issuer = "All"
             
    with col2:
        # Category Filter
        if 'Category' in available_cols:
             categories = ["All"] + sorted([str(x) for x in df['Category'].dropna().unique() if x != "N/A"])
             selected_category = st.selectbox("Asset Category", options=categories)
        else:
             selected_category = "All"
             
    with col3:
        # Currency Filter
        if 'Currency' in available_cols:
             currencies = ["All"] + sorted([str(x) for x in df['Currency'].dropna().unique() if x != "N/A"])
             selected_currency = st.selectbox("Currency", options=currencies)
        else:
             selected_currency = "All"

    st.write("")
    search_text = st.text_input("Search by Ticker or Name", placeholder="e.g. VTI, Vanguard, Technology...")
    
    st.divider()
    
    # Apply Filters
    filtered_df = df.copy()
    
    if selected_issuer != "All":
        filtered_df = filtered_df[filtered_df['Issuer'] == selected_issuer]
        
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
        
    if selected_currency != "All":
        filtered_df = filtered_df[filtered_df['Currency'] == selected_currency]
        
    if search_text:
        search_query = search_text.lower()
        # Search across Ticker and Name
        mask = (
            filtered_df['Ticker'].astype(str).str.lower().str.contains(search_query) | 
            filtered_df['Name'].astype(str).str.lower().str.contains(search_query)
        )
        filtered_df = filtered_df[mask]

    # Display Results
    st.markdown(f"#### Results: {len(filtered_df):,} ETFs Found")
    
    # Clean up display columns
    display_cols = [c for c in ['Ticker', 'Name', 'Issuer', 'Category', 'Currency', 'Exchange', 'Market'] if c in filtered_df.columns]
    
    if not filtered_df.empty:
         st.dataframe(
             filtered_df[display_cols],
             use_container_width=True,
             hide_index=True,
             height=600
         )
    else:
         st.info("No ETFs match your current filter criteria.")

if __name__ == "__main__":
    sidebar_nav("Screener")
    render_screener()
