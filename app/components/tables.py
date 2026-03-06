import streamlit as st
import pandas as pd
import uuid

def data_table(df, highlight_cols=None, format_dict=None, table_key=None):
    """Styled pandas dataframe with modern presentation"""
    if df.empty:
        st.warning("No data available to display.")
        return

    # Render a copy to prevent mutating the original dataframe
    display_df = df.copy()

    # Basic formatting
    if format_dict:
        for col, fmt in format_dict.items():
            if col in display_df.columns:
                display_df[col] = display_df[col].map(fmt.format)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # Download button
    csv = display_df.to_csv(index=False).encode('utf-8')
    key_val = table_key if table_key else f"download_{uuid.uuid4().hex}"
    st.download_button(
        label="⬇ Export CSV",
        data=csv,
        file_name='mudric_export.csv',
        mime='text/csv',
        key=key_val
    )
