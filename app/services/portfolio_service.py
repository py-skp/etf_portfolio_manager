from sqlalchemy.orm import Session
from ..database.models import Portfolio, Holding, Transaction
from .data_provider import DataProvider
import pandas as pd

class PortfolioService:
    @staticmethod
    def get_portfolios(db: Session):
        return db.query(Portfolio).all()

    @staticmethod
    def create_portfolio(db: Session, name: str, description: str = "", currency: str = "USD", benchmark: str = "SPY"):
        new_portfolio = Portfolio(
            name=name,
            description=description,
            currency=currency,
            benchmark_ticker=benchmark
        )
        db.add(new_portfolio)
        db.commit()
        db.refresh(new_portfolio)
        return new_portfolio

    @staticmethod
    def delete_portfolio(db: Session, portfolio_id: int):
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if portfolio:
            db.delete(portfolio)
            db.commit()
            return True
        return False

    @staticmethod
    def add_holding(db: Session, portfolio_id: int, ticker: str, name: str = "", asset_type: str = "ETF", target_pct: float = 0.0):
        # Prevent duplicate tickers in the same portfolio
        existing = db.query(Holding).filter(Holding.portfolio_id == portfolio_id, Holding.ticker == ticker).first()
        if existing:
            return None
            
        new_holding = Holding(
            portfolio_id=portfolio_id,
            ticker=ticker,
            name=name,
            asset_type=asset_type,
            target_allocation_pct=target_pct
        )
        db.add(new_holding)
        db.commit()
        db.refresh(new_holding)
        return new_holding

    @staticmethod
    def delete_holding(db: Session, holding_id: int):
        holding = db.query(Holding).filter(Holding.id == holding_id).first()
        if holding:
            db.delete(holding)
            db.commit()
            return True
        return False

    @staticmethod
    def bulk_import_transactions(db: Session, portfolio_id: int, transactions_data: list):
        """
        Expects a list of dicts: [{'ticker': 'AAPL', 'date': datetime, 'type': 'BUY', 'quantity': 10, 'price': 150.0}]
        """
        import_count = 0
        for data in transactions_data:
            ticker = data['ticker'].upper()
            
            # 1. Ensure holding exists
            holding = db.query(Holding).filter(Holding.portfolio_id == portfolio_id, Holding.ticker == ticker).first()
            if not holding:
                holding = Holding(
                    portfolio_id=portfolio_id,
                    ticker=ticker,
                    name=ticker, # Default to ticker if name unknown
                    asset_type="ETF",
                    target_allocation_pct=0.0
                )
                db.add(holding)
                db.commit()
                db.refresh(holding)
            
            # 2. Add transaction
            new_t = Transaction(
                portfolio_id=portfolio_id,
                holding_id=holding.id,
                transaction_type=data['type'],
                quantity=data['quantity'],
                price=data['price'],
                date=data['date']
            )
            db.add(new_t)
            import_count += 1
            
        db.commit()
        return import_count

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int):
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            db.delete(transaction)
            db.commit()
            return True
        return False

    @staticmethod
    def get_portfolio_valuation(db: Session, portfolio_id: int):
        """Calculate current valuation of the portfolio"""
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        
        valuation_data = []
        total_value = 0
        
        for holding in holdings:
            # Get latest price
            current_price = DataProvider.get_current_price(holding.ticker) or 0
            
            # Calculate quantity from transactions
            transactions = db.query(Transaction).filter(Transaction.holding_id == holding.id).all()
            total_qty = sum(t.quantity if t.transaction_type == "BUY" else -t.quantity for t in transactions)
            
            market_value = total_qty * current_price
            total_value += market_value
            
            valuation_data.append({
                "ticker": holding.ticker,
                "name": holding.name,
                "quantity": total_qty,
                "price": current_price,
                "market_value": market_value,
                "weight": 0 # Calculate later
            })
            
        # Calculate weights
        if total_value > 0:
            for item in valuation_data:
                item["weight"] = (item["market_value"] / total_value) * 100
                
        return {
            "total_value": total_value,
            "holdings": valuation_data
        }
