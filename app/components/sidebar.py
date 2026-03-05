import streamlit as st
from streamlit_option_menu import option_menu

def sidebar_nav(default_page="Dashboard"):
    with st.sidebar:
        st.title("Mudric Lab")
        st.markdown("---")
        
        # Portfolio Summary in Sidebar
        st.sidebar.subheader("Portfolio Summary")
        st.sidebar.metric("Total Value", "$124,500", "+2.5%")
        
        st.markdown("---")
        
        # Define menu structure and mapping to files
        menu_items = {
            "Dashboard": "main.py",
            "Portfolio": "pages/01_portfolio.py",
            "ETF Intelligence": "pages/02_etf_intelligence.py",
            "Performance": "pages/04_performance.py",
            "Risk": "pages/05_risk.py",
            "Strategy": None,
            "Screener": None,
            "Macro": None,
            "Reports": None,
            "Settings": "pages/03_settings.py"
        }
        
        options = list(menu_items.keys())
        icons = ["house", "briefcase", "graph-up", "speedometer", "shield-exclamation", "gear", "search", "globe", "file-earmark-text", "gear-fill"]
        
        try:
            default_index = options.index(default_page)
        except ValueError:
            default_index = 0
            
        # Determine from context if `default_page` is not provided correctly or running natively
        try:
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            ctx = get_script_run_ctx()
            script_path = ctx.main_script_path if ctx else ""
            if "04_performance" in script_path:
                default_index = options.index("Performance")
            elif "05_risk" in script_path:
                default_index = options.index("Risk")
        except:
            pass

        selected = option_menu(
            menu_title="Main Menu",
            options=options,
            icons=icons,
            menu_icon="cast",
            default_index=default_index,
            styles={
                "container": {"background-color": "#1A1A2E"},
                "icon": {"color": "#D4A017", "font-size": "1.2rem"}, 
                "nav-link": {"font-size": "1rem", "text-align": "left", "margin":"0px", "--hover-color": "#262730"},
                "nav-link-selected": {"background-color": "#D4A017", "color": "#0F1117"},
            }
        )
        
        # Handle Navigation
        if selected != options[default_index]:
            target_file = menu_items.get(selected)
            if target_file:
                st.switch_page(target_file)
            else:
                st.toast(f"The {selected} module is planned for a future phase.", icon="🚀")
        
        return selected
