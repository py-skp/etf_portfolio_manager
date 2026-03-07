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
        """Calculate current valuation, gains/losses (Realized & Unrealized) using WAC"""
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        
        valuation_data = []
        total_value = 0
        total_unrealized_gl = 0
        total_realized_gl = 0
        
        for holding in holdings:
            # Get latest price
            current_price = DataProvider.get_current_price(holding.ticker) or 0
            
            # Performance tracking logic (WAC)
            transactions = db.query(Transaction).filter(Transaction.holding_id == holding.id).order_by(Transaction.date.asc()).all()
            
            shares = 0
            avg_cost = 0
            realized_gl = 0
            total_cost_basis = 0 # total_cost_basis for current shares
            
            for t in transactions:
                t_qty = float(t.quantity)
                t_price = float(t.price)
                
                if t.transaction_type == "BUY":
                    # Update WAC
                    new_total_cost = (shares * avg_cost) + (t_qty * t_price)
                    shares += t_qty
                    if shares > 0:
                        avg_cost = new_total_cost / shares
                        total_cost_basis = shares * avg_cost
                elif t.transaction_type == "SELL":
                    # Realize gain/loss
                    realized_gl += (t_price - avg_cost) * t_qty
                    shares -= t_qty
                    # Cost basis for remaining shares decreases proportionally
                    total_cost_basis = shares * avg_cost
            
            market_value = shares * current_price
            unrealized_gl = (current_price - avg_cost) * shares if shares > 0 else 0
            
            total_value += market_value
            total_unrealized_gl += unrealized_gl
            total_realized_gl += realized_gl
            
            valuation_data.append({
                "ticker": holding.ticker,
                "name": holding.name,
                "quantity": shares,
                "price": current_price,
                "avg_cost": avg_cost,
                "market_value": market_value,
                "unrealized_gl": unrealized_gl,
                "realized_gl": realized_gl,
                "weight": 0 # Calculate later
            })
            
        # Calculate weights
        if total_value > 0:
            for item in valuation_data:
                item["weight"] = (item["market_value"] / total_value) * 100
                
        return {
            "total_value": total_value,
            "total_unrealized_gl": total_unrealized_gl,
            "total_realized_gl": total_realized_gl,
            "holdings": valuation_data
        }

    @staticmethod
    def get_total_valuation(db: Session):
        """Calculate the sum of all portfolio valuations for the sidebar"""
        portfolios = db.query(Portfolio).all()
        grand_total = 0
        for p in portfolios:
            val = PortfolioService.get_portfolio_valuation(db, p.id)
            grand_total += val['total_value']
        return grand_total

    @staticmethod
    def get_portfolio_history(db: Session, portfolio_id: int):
        """Reconstruct historical valuation comparing Invested Capital vs Market Value"""
        val_res = PortfolioService.get_portfolio_valuation(db, portfolio_id)
        current_val = val_res['total_value']
        
        transactions = db.query(Transaction).filter(Transaction.portfolio_id == portfolio_id).order_by(Transaction.date.asc()).all()
        import pandas as pd
        from datetime import datetime, timedelta
        
        if not transactions:
            return pd.DataFrame()
            
        start_date = transactions[0].date
        end_date = datetime.now()
        
        # If the first transaction was today, just return a single point
        if (end_date - start_date).days < 1:
            return pd.DataFrame([{
                "Date": end_date, 
                "Invested Capital": current_val, 
                "Market Value": current_val
            }])

        # Calculate Total Cost Basis
        # We can sum up (quantity * avg_cost) from the holdings, or simplify by netting cash flows.
        # For a clean chart, we'll track cumulative net cash flow (principal).
        total_principal = sum((t.price * t.quantity) if t.transaction_type == "BUY" else -(t.price * t.quantity) for t in transactions)
        
        # Total ROI
        if total_principal > 0:
            total_gain_pct = (current_val - total_principal) / total_principal
        else:
            total_gain_pct = 0.0
            
        total_days = (end_date - start_date).days
        daily_gain_pct = total_gain_pct / total_days if total_days > 0 else 0
        
        # Generate roughly monthly points for performance
        dates = pd.date_range(start=start_date, end=end_date, freq="W")
        # Ensure end date is included
        if len(dates) == 0 or dates[-1] != end_date:
            dates = dates.append(pd.DatetimeIndex([end_date]))
            
        history = []
        for d in dates:
            # Principal up to this date
            past_txs = [t for t in transactions if t.date <= d]
            invested = sum((t.price * t.quantity) if t.transaction_type == "BUY" else -(t.price * t.quantity) for t in past_txs)
            
            # Prorated gain
            days_passed = (d - start_date).days
            prorated_gain = daily_gain_pct * days_passed
            
            est_market_value = invested * (1 + prorated_gain)
            
            # Guarantee the last point perfectly matches the real live dashboard value
            if d == end_date:
                est_market_value = current_val
                
            history.append({
                "Date": d,
                "Invested Capital": invested,
                "Market Value": est_market_value
            })
            
        return pd.DataFrame(history)
