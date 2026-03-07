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

@st.dialog("Confirm Deletion")
def confirm_delete_holding(db_session, holding_id, ticker):
    st.warning(f"Are you sure you want to delete {ticker}?\n\nThis will also permanently delete all of its recorded transactions.")
    if st.button("Yes, Delete Holding", type="primary"):
        PortfolioService.delete_holding(db_session, holding_id)
        st.session_state.holding_deleted = True
        st.rerun()

@st.dialog("Confirm Deletion")
def confirm_delete_transaction(db_session, t_id, desc):
    st.warning(f"Are you sure you want to delete this transaction: {desc}?")
    if st.button("Yes, Delete Transaction", type="primary"):
        PortfolioService.delete_transaction(db_session, t_id)
        st.session_state.transaction_deleted = True
        st.rerun()

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
                st.markdown("<br>", unsafe_allow_html=True)
                # Header row
                hc1, hc2, hc3, hc4, hc5 = st.columns([1, 2, 4, 2, 1])
                hc1.write("**ID**")
                hc2.write("**Ticker**")
                hc3.write("**Name**")
                hc4.write("**Target %**")
                hc5.write("**Action**")
                st.divider()
                
                for h in holdings:
                    c1, c2, c3, c4, c5 = st.columns([1, 2, 4, 2, 1])
                    c1.write(h.id)
                    c2.write(h.ticker)
                    c3.write(h.name)
                    c4.write(h.target_allocation_pct)
                    if c5.button("🗑️", key=f"del_h_{h.id}"):
                        confirm_delete_holding(db, h.id, h.ticker)
                        
                if st.session_state.pop("holding_deleted", False):
                    st.toast("Holding deleted successfully!")
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
                st.markdown("<br>", unsafe_allow_html=True)
                # Header row
                tc1, tc2, tc3, tc4, tc5, tc6 = st.columns([1, 2, 2, 1.5, 1.5, 1])
                tc1.write("**Date**")
                tc2.write("**Ticker**")
                tc3.write("**Type**")
                tc4.write("**Qty**")
                tc5.write("**Price**")
                tc6.write("**Action**")
                st.divider()
                
                for t in transactions:
                    dt_str = t.date.strftime("%Y-%m-%d")
                    c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 1.5, 1.5, 1])
                    c1.write(dt_str)
                    c2.write(t.holding.ticker)
                    c3.write(t.transaction_type)
                    c4.write(t.quantity)
                    c5.write(f"${t.price:.2f}")
                    if c6.button("🗑️", key=f"del_t_{t.id}"):
                        desc = f"{dt_str} {t.transaction_type} {t.quantity} {t.holding.ticker}"
                        confirm_delete_transaction(db, t.id, desc)
                        
                if st.session_state.pop("transaction_deleted", False):
                    st.toast("Transaction deleted successfully!")
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
