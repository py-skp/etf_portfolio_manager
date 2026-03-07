import streamlit as st
st.set_page_config(page_title="Mudric Lab — Portfolio Intelligence", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
from app.components.sidebar import sidebar_nav
from app.components.styles import inject_global_css
from app.components.metrics import section_header
from app.components.tables import data_table
from app.database.connection import SessionLocal
from app.database.models import Portfolio, Holding, Transaction
from app.services.portfolio_service import PortfolioService
from datetime import datetime

# NOTE: This page is typically accessed via the sidebar_nav in main.py 
# but Streamlit multipage setup usually expects files in pages/

def render_portfolio_mgmt():
    section_header("Portfolio Management", "Build and organize your investment universes.")
    
    db = SessionLocal()
    
    # Portfolio Selector/Creator
    col1, col2 = st.columns([3, 1])
    with col1:
        portfolios = PortfolioService.get_portfolios(db)
        
        # Maintain active portfolio state across reruns robustly
        if 'active_portfolio_id' not in st.session_state:
            st.session_state.active_portfolio_id = portfolios[0].id if portfolios else None
            
        if 'newly_created_portfolio_id' in st.session_state:
            st.session_state.active_portfolio_id = st.session_state.newly_created_portfolio_id
            del st.session_state.newly_created_portfolio_id

        select_index = 0
        if st.session_state.active_portfolio_id:
            for i, p in enumerate(portfolios):
                if p.id == st.session_state.active_portfolio_id:
                    select_index = i
                    break

        def on_portfolio_change():
            selected_p = st.session_state.portfolio_selector
            if selected_p:
                st.session_state.active_portfolio_id = selected_p.id

        selected_portfolio = st.selectbox(
            "Portfolio", 
            options=portfolios, 
            format_func=lambda x: x.name, 
            index=select_index,
            key="portfolio_selector",
            on_change=on_portfolio_change
        )
    
    with col2:
        with st.popover("+ New Portfolio", use_container_width=True):
            with st.form("new_portfolio_form"):
                name = st.text_input("Portfolio Name")
                desc = st.text_area("Description")
                submitted = st.form_submit_button("Create")
                if submitted and name:
                    new_p = PortfolioService.create_portfolio(db, name, desc)
                    st.session_state.newly_created_portfolio_id = new_p.id
                    st.success(f"Portfolio '{name}' created!")
                    st.rerun()

    if selected_portfolio:
        tab1, tab2, tab3 = st.tabs(["Holdings", "Transactions", "Import CSV"])
        
        with tab1:
            st.subheader("Manage Holdings")
            with st.expander("Add New Holding"):
                with st.form("add_holding_form"):
                    ticker = st.text_input("Ticker (e.g. VTI)")
                    name = st.text_input("Asset Name")
                    target = st.number_input("Target Allocation %", min_value=0.0, max_value=100.0)
                    submitted = st.form_submit_button("Add Holding")
                    if submitted and ticker:
                        h = PortfolioService.add_holding(db, selected_portfolio.id, ticker.upper(), name, target_pct=target)
                        if h:
                            st.success(f"Added {ticker}")
                            st.rerun()
                        else:
                            st.error(f"Ticker {ticker.upper()} already exists in this portfolio.")
            
            # Show existing holdings
            holdings = db.query(Holding).filter(Holding.portfolio_id == selected_portfolio.id).all()
            if holdings:
                df_h = pd.DataFrame([{
                    "ID": h.id,
                    "Ticker": h.ticker,
                    "Name": h.name,
                    "Target %": h.target_allocation_pct
                } for h in holdings])
                data_table(df_h)
                
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("Delete Holding"):
                    st.warning("Deleting a holding will also delete all of its recorded transactions.")
                    h_options = {h.id: f"{h.ticker} - {h.name}" for h in holdings}
                    h_to_delete = st.selectbox("Select Holding to Delete", options=list(h_options.keys()), format_func=lambda x: h_options[x])
                    if st.button("Delete Selected Holding", type="primary"):
                        if PortfolioService.delete_holding(db, h_to_delete):
                            st.success("Holding deleted!")
                            st.rerun()
            else:
                st.info("No holdings yet.")

        with tab2:
            st.subheader("Transaction History")
            with st.expander("Record Transaction"):
                # Simplified form for Phase 1
                with st.form("transaction_form"):
                    h_ticker = st.selectbox("Holding", options=[h.ticker for h in holdings]) if holdings else None
                    t_type = st.selectbox("Type", options=["BUY", "SELL"])
                    qty = st.number_input("Quantity", min_value=0.0)
                    price = st.number_input("Price", min_value=0.0)
                    date = st.date_input("Date", value=datetime.today())
                    
                    submitted = st.form_submit_button("Record")
                    if submitted and h_ticker:
                        h = db.query(Holding).filter(Holding.portfolio_id == selected_portfolio.id, Holding.ticker == h_ticker).first()
                        if h:
                            new_t = Transaction(
                            portfolio_id=selected_portfolio.id,
                            holding_id=h.id,
                            transaction_type=t_type,
                            quantity=qty,
                            price=price,
                            date=datetime.combine(date, datetime.min.time())
                        )
                        db.add(new_t)
                        db.commit()
                        st.success("Transaction recorded!")
                        st.rerun()
            
            # List transactions
            transactions = db.query(Transaction).filter(Transaction.portfolio_id == selected_portfolio.id).all()
            if transactions:
                df_t = pd.DataFrame([{
                    "ID": t.id,
                    "Date": t.date.strftime("%Y-%m-%d"),
                    "Ticker": t.holding.ticker,
                    "Type": t.transaction_type,
                    "Qty": t.quantity,
                    "Price": f"${t.price:.2f}",
                } for t in transactions])
                data_table(df_t)
                
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("Delete Transaction"):
                    t_options = {t.id: f"{t.date.strftime('%Y-%m-%d')} - {t.transaction_type} {t.quantity} {t.holding.ticker} @ ${t.price:.2f}" for t in transactions}
                    t_to_delete = st.selectbox("Select Transaction to Delete", options=list(t_options.keys()), format_func=lambda x: t_options[x])
                    if st.button("Delete Selected Transaction", type="primary"):
                        if PortfolioService.delete_transaction(db, t_to_delete):
                            st.success("Transaction deleted!")
                            st.rerun()
            else:
                st.info("No transactions found.")

        with tab3:
            st.subheader("Import Portfolios")
            st.file_uploader("Upload CSV (Coming Soon in Phase 6)", type=["csv"])
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.expander("Danger Zone"):
            st.warning("Deleting a portfolio will permanently remove all its holdings and transactions.")
            if st.button("Delete This Portfolio", type="primary"):
                PortfolioService.delete_portfolio(db, selected_portfolio.id)
                st.session_state.active_portfolio_id = None
                st.success("Portfolio deleted.")
                st.rerun()

    db.close()

if __name__ == "__main__":
    # If run as a page in streamlit multipage
    from app.components.sidebar import sidebar_nav
    from app.components.styles import inject_global_css
    inject_global_css()
    sidebar_nav("Portfolio")
    render_portfolio_mgmt()
