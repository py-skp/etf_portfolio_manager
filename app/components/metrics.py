import streamlit as st

def metric_card(label, value, delta=None, delta_color="normal", icon=None, subtitle=None):
    """
    Styled KPI metric card
    delta_color: "normal" (green for positive, red for negative), "inverse" (red for positive, green for negative), or "off"
    """
    with st.container():
        # Handle delta coloration
        d_color = "#94A3B8"
        if delta and delta_color != "off":
            try:
                d_val = float(str(delta).replace("%", "").replace("+", "").replace(",", ""))
                if delta_color == "normal":
                    d_color = "#28a745" if d_val > 0 else "#dc3545"
                elif delta_color == "inverse":
                    d_color = "#dc3545" if d_val > 0 else "#28a745"
            except:
                pass

        st.markdown(f"""
        <div style="
            background-color: #1A1A2E;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #D4A017;
            margin-bottom: 10px;
        ">
            <p style="color: #F3F4F6; font-size: 0.8rem; margin-bottom: 5px;">{icon if icon else ''} {label}</p>
            <h3 style="color: #D4A017; margin: 0;">{value}</h3>
            {f'<p style="color: #94A3B8; font-size: 0.85rem; margin-top: 5px; font-style: italic;">{subtitle}</p>' if subtitle else ''}
            {f'<p style="color: {d_color}; font-size: 0.9rem; margin-top: 5px;">{delta}</p>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

def section_header(title, subtitle=None, badge=None):
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"*{subtitle}*")
    if badge:
        st.info(badge)
    st.divider()
