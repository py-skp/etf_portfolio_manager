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
    def add_holding(db: Session, portfolio_id: int, ticker: str, name: str = "", asset_type: str = "ETF", target_pct: float = 0.0):
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
