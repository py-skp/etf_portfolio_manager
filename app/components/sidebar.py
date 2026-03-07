import streamlit as st
from streamlit_option_menu import option_menu
from app.database.connection import SessionLocal
from app.services.portfolio_service import PortfolioService
import base64
from pathlib import Path


def sidebar_nav(default_page="Dashboard"):
    with st.sidebar:
        # Logo area with image
        logo_path = Path("app/assets/logo.png")
        logo_b64 = ""
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()

        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 1.25rem 0 0.75rem 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        ">
            <img src="data:image/png;base64,{logo_b64}" style="
                width: 85px; 
                margin-bottom: 2px;
                filter: invert(1) brightness(0.9);
                mix-blend-mode: screen;
            ">
            <h1 style="
                font-family: 'Inter', sans-serif;
                font-weight: 800;
                font-size: 1.6rem;
                letter-spacing: -0.02em;
                margin: 0;
                background: linear-gradient(135deg, #E8EAED 0%, #9CA3AF 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">Mudric Lab</h1>
            <p style="color: #00D4AA; font-size: 0.65rem; margin: 2px 0 0 0; letter-spacing: 0.15em; text-transform: uppercase; font-weight: 600;">
                Portfolio Intelligence
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent); margin: 0.5rem 0;"></div>', unsafe_allow_html=True)
        
        # Portfolio Summary Widget
        db = SessionLocal()
        try:
            total_val = PortfolioService.get_total_valuation(db)
            formatted_val = f"${total_val:,.0f}"
        except:
            formatted_val = "$0"
        finally:
            db.close()

        st.markdown(f"""
        <div style="
            background: rgba(0, 212, 170, 0.06);
            border: 1px solid rgba(0, 212, 170, 0.12);
            border-radius: 10px;
            padding: 12px 14px;
            margin: 0.5rem 0;
        ">
            <div style="color: #6B7280; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;">Portfolio Value</div>
            <div style="color: #E8EAED; font-size: 1.3rem; font-weight: 700; margin: 4px 0 2px 0;">{formatted_val}</div>
            <div style="color: #00D4AA; font-size: 0.75rem; font-weight: 500; cursor: help;" title="Market data is fetched via standard APIs and cached to prevent rate limits. Prices automatically refresh hourly, or manually using the refresh button below.">
                [+] Current Value (i)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent); margin: 0.5rem 0;"></div>', unsafe_allow_html=True)

        # Define menu structure
        menu_items = {
            "Dashboard": "main.py",
            "Portfolio": "pages/01_portfolio.py",
            "ETF Intelligence": "pages/02_etf_intelligence.py",
            "Performance": "pages/04_performance.py",
            "Risk": "pages/05_risk.py",
            "Strategy": "pages/06_strategy.py",
            "Screener": "pages/07_screener.py",
            "Macro": "pages/08_macro.py",
            "Reports": "pages/09_reports.py",
            "Settings": "pages/03_settings.py"
        }
        
        options = list(menu_items.keys())
        icons = ["house", "briefcase", "graph-up", "speedometer2", "shield-check", "lightbulb", "search", "globe2", "file-earmark-bar-graph", "gear"]
        
        try:
            default_index = options.index(default_page)
        except ValueError:
            default_index = 0
            
        try:
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            ctx = get_script_run_ctx()
            script_path = ctx.main_script_path if ctx else ""
            if "04_performance" in script_path:
                default_index = options.index("Performance")
            elif "05_risk" in script_path:
                default_index = options.index("Risk")
            elif "06_strategy" in script_path:
                default_index = options.index("Strategy")
            elif "07_screener" in script_path:
                default_index = options.index("Screener")
            elif "08_macro" in script_path:
                default_index = options.index("Macro")
            elif "09_reports" in script_path:
                default_index = options.index("Reports")
        except:
            pass

        selected = option_menu(
            menu_title=None,
            options=options,
            icons=icons,
            default_index=default_index,
            styles={
                "container": {
                    "background-color": "transparent",
                    "padding": "0",
                },
                "icon": {
                    "color": "#9CA3AF",
                    "font-size": "1rem",
                },
                "nav-link": {
                    "font-family": "'Inter', sans-serif",
                    "font-size": "0.85rem",
                    "font-weight": "500",
                    "text-align": "left",
                    "margin": "2px 0",
                    "padding": "10px 14px",
                    "border-radius": "8px",
                    "color": "#9CA3AF",
                    "--hover-color": "rgba(0, 212, 170, 0.06)",
                    "transition": "all 0.2s ease",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, rgba(0,212,170,0.15) 0%, rgba(59,130,246,0.10) 100%)",
                    "color": "#00D4AA",
                    "font-weight": "600",
                    "border-left": "3px solid #00D4AA",
                },
            }
        )
        
        # Handle Navigation
        if selected != options[default_index]:
            target_file = menu_items.get(selected)
            if target_file:
                st.switch_page(target_file)
            else:
                st.toast(f"The {selected} module is planned for a future phase.", icon="🚀")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Market Data", use_container_width=True, help="Force-fetch the latest prices by clearing cached data"):
            from app.services.cache_service import cache_service
            cache_service.clear_all()
            st.toast("Market data cache cleared. Fetching latest prices...", icon="✅")
            st.rerun()

        # Footer
        st.markdown("""
        <div style="
            position: fixed; bottom: 0; left: 0; width: inherit; 
            padding: 12px 20px;
            border-top: 1px solid rgba(255,255,255,0.05);
            background: linear-gradient(180deg, transparent, #0D1117);
        ">
            <p style="color: #4B5563; font-size: 0.65rem; text-align: center; margin: 0;">
                Built by Mudric Lab · v2.0
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        return selected
