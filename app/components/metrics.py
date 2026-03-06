import streamlit as st

def metric_card(label, value, delta=None, delta_color="normal", icon=None, subtitle=None):
    """
    Glassmorphic KPI metric card — pure HTML with no JS event handlers (avoids Streamlit escaping).
    delta_color: "normal" (green up, red down), "inverse" (red up, green down), or "off"
    """
    d_color = "#9CA3AF"
    arrow = ""

    if delta and delta_color != "off":
        try:
            d_val = float(
                str(delta).replace("%", "").replace("+", "").replace(",", "")
                .replace("bps", "").replace("$", "").strip().split()[0]
            )
            if delta_color == "normal":
                d_color = "#00D4AA" if d_val > 0 else "#EF4444"
            elif delta_color == "inverse":
                d_color = "#EF4444" if d_val > 0 else "#00D4AA"
            arrow = "▲" if d_val > 0 else ("▼" if d_val < 0 else "")
        except Exception:
            pass

    delta_block = (
        f'<div style="color:{d_color};font-size:0.78rem;font-weight:600;margin-top:5px;">'
        f'{arrow}&nbsp;{delta}</div>'
    ) if delta else ""

    subtitle_block = (
        f'<div style="color:#6B7280;font-size:0.70rem;margin-top:3px;font-style:italic;">'
        f'{subtitle}</div>'
    ) if subtitle else ""

    icon_block = f'<span style="margin-right:5px;">{icon}</span>' if icon else ""

    html = f"""
<div style="
    background:rgba(19,23,34,0.65);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:12px;
    padding:1.1rem 1.2rem;
    margin-bottom:0.6rem;
    position:relative;
    overflow:hidden;
">
  <div style="position:absolute;top:0;left:0;width:3px;height:100%;
    background:linear-gradient(180deg,#00D4AA 0%,#3B82F6 100%);
    border-radius:3px 0 0 3px;"></div>
  <div style="color:#9CA3AF;font-size:0.72rem;font-weight:600;
    text-transform:uppercase;letter-spacing:0.07em;margin-bottom:5px;">
    {icon_block}{label}
  </div>
  <div style="color:#E8EAED;font-size:1.4rem;font-weight:700;letter-spacing:-0.02em;line-height:1.2;">
    {value}
  </div>
  {subtitle_block}
  {delta_block}
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def section_header(title, subtitle=None, badge=None):
    """Modern section header with an animated gradient underline accent."""
    sub_html = (
        f'<p style="color:#9CA3AF;font-size:0.9rem;margin-top:0;font-weight:400;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(f"""
<div style="margin-bottom:0.25rem;">
  <h2 style="color:#E8EAED;font-family:'Inter',sans-serif;font-weight:700;
    font-size:1.6rem;margin-bottom:0.2rem;letter-spacing:-0.03em;">
    {title}
  </h2>
  {sub_html}
</div>
<div style="height:3px;background:linear-gradient(90deg,#00D4AA,#3B82F6,#00D4AA);
  background-size:200% auto;border-radius:2px;margin-bottom:1.5rem;"></div>
""", unsafe_allow_html=True)
    if badge:
        st.info(badge)
