import streamlit as st
import pandas as pd
import uuid

def data_table(df, highlight_cols=None, format_dict=None, table_key=None):
    """Styled pandas dataframe"""
    if df.empty:
        st.warning("No data available to display.")
        return

    # Basic formatting
    if format_dict:
        for col, fmt in format_dict.items():
            if col in df.columns:
                df[col] = df[col].map(fmt.format)

    # Display using Streamlit's native styled dataframe or AgGrid
    # For Phase 1, we'll use st.dataframe with styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    key_val = table_key if table_key else f"download_{uuid.uuid4().hex}"
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='mudric_export.csv',
        mime='text/csv',
        key=key_val
    )
