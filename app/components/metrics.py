import streamlit as st

def metric_card(label, value, delta=None, delta_color="normal", icon=None, subtitle=None):
    """
    Glassmorphic KPI metric card with hover effects.
    delta_color: "normal" (green up, red down), "inverse" (red up, green down), or "off"
    """
    # Determine delta color
    d_color = "#9CA3AF"
    if delta and delta_color != "off":
        try:
            d_val = float(str(delta).replace("%", "").replace("+", "").replace(",", "").replace("bps", "").strip().split()[0])
            if delta_color == "normal":
                d_color = "#00D4AA" if d_val > 0 else "#EF4444"
            elif delta_color == "inverse":
                d_color = "#EF4444" if d_val > 0 else "#00D4AA"
        except:
            pass

    # Build the delta arrow
    delta_html = ""
    if delta:
        try:
            d_val = float(str(delta).replace("%", "").replace("+", "").replace(",", "").replace("bps", "").strip().split()[0])
            arrow = "▲" if d_val > 0 else "▼" if d_val < 0 else ""
        except:
            arrow = ""
        delta_html = f'<div style="color: {d_color}; font-size: 0.8rem; font-weight: 500; margin-top: 6px;">{arrow} {delta}</div>'

    subtitle_html = f'<div style="color: #6B7280; font-size: 0.7rem; margin-top: 4px; font-style: italic;">{subtitle}</div>' if subtitle else ''
    icon_html = f'<span style="margin-right: 4px;">{icon}</span>' if icon else ''

    st.markdown(f"""
    <div style="
        background: rgba(19, 23, 34, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.15rem 1.25rem;
        margin-bottom: 0.65rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    " onmouseover="this.style.borderColor='rgba(0,212,170,0.3)';this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 32px rgba(0,212,170,0.08)'"
       onmouseout="this.style.borderColor='rgba(255,255,255,0.06)';this.style.transform='translateY(0)';this.style.boxShadow='none'">
        <div style="
            position: absolute; top: 0; left: 0; width: 3px; height: 100%;
            background: linear-gradient(180deg, #00D4AA 0%, #3B82F6 100%);
            border-radius: 3px 0 0 3px;
        "></div>
        <div style="color: #9CA3AF; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
            {icon_html}{label}
        </div>
        <div style="color: #E8EAED; font-size: 1.4rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.2;">
            {value}
        </div>
        {subtitle_html}
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def section_header(title, subtitle=None, badge=None):
    """Modern section header with gradient underline accent"""
    st.markdown(f"""
    <div style="margin-bottom: 0.25rem;">
        <h2 style="color: #E8EAED; font-family: 'Inter', sans-serif; font-weight: 700; font-size: 1.6rem; margin-bottom: 0.25rem; letter-spacing: -0.03em;">
            {title}
        </h2>
        {f'<p style="color: #9CA3AF; font-size: 0.9rem; margin-top: 0; font-weight: 400;">{subtitle}</p>' if subtitle else ''}
    </div>
    <div style="
        height: 3px;
        background: linear-gradient(90deg, #00D4AA, #3B82F6, #00D4AA);
        background-size: 200% auto;
        animation: gradient-flow 3s ease infinite;
        border-radius: 2px;
        margin-bottom: 1.5rem;
    "></div>
    """, unsafe_allow_html=True)
    if badge:
        st.info(badge)
