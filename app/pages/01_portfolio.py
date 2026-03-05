import streamlit as st
import pandas as pd
from app.components.sidebar import sidebar_nav
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
        selected_portfolio = st.selectbox("Portfolio", options=portfolios, format_func=lambda x: x.name)
    
    with col2:
        if st.button("+ New Portfolio"):
            # This would normally be a modal or expansion
            with st.form("new_portfolio_form"):
                name = st.text_input("Portfolio Name")
                desc = st.text_area("Description")
                submitted = st.form_submit_button("Create")
                if submitted and name:
                    PortfolioService.create_portfolio(db, name, desc)
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
                        PortfolioService.add_holding(db, selected_portfolio.id, ticker.upper(), name, target_pct=target)
                        st.success(f"Added {ticker}")
                        st.rerun()
            
            # Show existing holdings
            holdings = db.query(Holding).filter(Holding.portfolio_id == selected_portfolio.id).all()
            if holdings:
                df_h = pd.DataFrame([{
                    "Ticker": h.ticker,
                    "Name": h.name,
                    "Target %": h.target_allocation_pct
                } for h in holdings])
                data_table(df_h)
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
                        h = db.query(Holding).filter(Holding.ticker == h_ticker).first()
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
                    "Date": t.date,
                    "Ticker": t.holding.ticker,
                    "Type": t.transaction_type,
                    "Qty": t.quantity,
                    "Price": t.price,
                } for t in transactions])
                data_table(df_t)
            else:
                st.info("No transactions found.")

        with tab3:
            st.subheader("Import Portfolios")
            st.file_uploader("Upload CSV (Coming Soon in Phase 6)", type=["csv"])

    db.close()

if __name__ == "__main__":
    # If run as a page in streamlit multipage
    from app.components.sidebar import sidebar_nav
    sidebar_nav("Portfolio")
    render_portfolio_mgmt()
