# Mudric Lab — Portfolio Intelligence

Institutional-grade portfolio analysis. Open source. Free forever.

## What is this?
Mudric Lab is an open-source platform for finance professionals and serious investors to track portfolios, build strategies, and perform deep investment analytics. It combines the power of Python's financial ecosystem (yfinance, vectorbt, PyPortfolioOpt) with a modern Streamlit interface.

## Quick Start
Get the platform running in less than 2 minutes using Docker:

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/mudric-portfolio.git
   cd mudric-portfolio
   ```

2. **Setup environment**
   ```bash
   cp .env.example .env
   ```

3. **Start services**
   ```bash
   docker-compose up --build
   ```

4. **Seed demo data (Optional)**
   ```bash
   docker-compose exec streamlit python scripts/seed_data.py
   ```

Visit `http://localhost:8501` to access the dashboard.

## Features (Phase 1)
- **Portfolio Management**: Create portfolios, track holdings, and record transactions.
- **Executive Dashboard**: Real-time KPI metrics and allocation charts.
- **Unified Data Provider**: Integrated `yfinance` with Redis caching for high performance.
- **Dark Theme**: Premium institutional-grade UI/UX.

## Tech Stack
- **Frontend**: Streamlit
- **Database**: PostgreSQL 15
- **Caching**: Redis
- **Data**: yfinance
- **ORM**: SQLAlchemy
- **Deployment**: Docker Compose

## Roadmap
- **Phase 2**: ETF Intelligence & Comparison Tool
- **Phase 3**: Performance Analytics & Risk (VaR, Monte Carlo)
- **Phase 4**: Strategy Builder & Backtester (vectorbt)
- **Phase 5**: Apache Superset Integration
- **Phase 6**: PDF/Excel Reports & Macro Dashboard

## License
MIT License. Free forever. Built by Mudric Lab.
