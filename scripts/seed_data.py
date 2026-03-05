import sys
import os
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal, engine
from app.database.models import Base, Portfolio, Holding, Transaction

def seed_demo_data():
    print("Initializing database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Create Portfolio
    print("Creating Global Growth Portfolio...")
    portfolio = Portfolio(
        name="Global Growth Portfolio",
        description="A diversified institutional-grade demo portfolio.",
        currency="USD",
        benchmark_ticker="SPY",
        is_default=True
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    
    # 2. Add Holdings
    holdings_data = [
        ("VTI", "Vanguard Total Stock Market ETF", "ETF", 35.0),
        ("VXUS", "Vanguard Total International Stock ETF", "ETF", 25.0),
        ("BND", "Vanguard Total Bond Market ETF", "ETF", 20.0),
        ("QQQ", "Invesco QQQ Trust", "ETF", 10.0),
        ("GLD", "SPDR Gold Shares", "ETF", 5.0),
        ("VNQ", "Vanguard Real Estate ETF", "ETF", 5.0),
    ]
    
    holdings = []
    for ticker, name, a_type, target in holdings_data:
        h = Holding(
            portfolio_id=portfolio.id,
            ticker=ticker,
            name=name,
            asset_type=a_type,
            target_allocation_pct=target
        )
        db.add(h)
        holdings.append(h)
    
    db.commit()
    
    # 3. Add Transactions (Realistic 2-year history)
    print("Seeding transactions...")
    start_date = datetime.now() - timedelta(days=730)
    initial_capital = 100000.0
    
    for h in holdings:
        # Initial Buy
        target_allocation = h.target_allocation_pct / 100.0
        amount_to_invest = initial_capital * target_allocation
        
        # Mock price (real prices would be fetched, but for seed we use estimates)
        price_map = {"VTI": 200, "VXUS": 50, "BND": 75, "QQQ": 350, "GLD": 180, "VNQ": 85}
        price = price_map.get(h.ticker, 100)
        qty = amount_to_invest / price
        
        t = Transaction(
            portfolio_id=portfolio.id,
            holding_id=h.id,
            transaction_type="BUY",
            date=start_date,
            quantity=qty,
            price=price,
            notes="Initial investment"
        )
        db.add(t)
        
        # Add some quarterly rebalancing/buys
        for i in range(1, 8):
            buy_date = start_date + timedelta(days=i*90)
            if buy_date > datetime.now():
                break
                
            t_add = Transaction(
                portfolio_id=portfolio.id,
                holding_id=h.id,
                transaction_type="BUY",
                date=buy_date,
                quantity=random.uniform(1, 5),
                price=price * random.uniform(0.9, 1.2),
                notes="Quarterly contribution"
            )
            db.add(t_add)
            
    db.commit()
    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_demo_data()
