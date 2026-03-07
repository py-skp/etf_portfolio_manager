from sqlalchemy import text
from app.database.connection import engine

def migrate():
    print("Checking database schema for workspace isolation...")
    with engine.connect() as conn:
        # Check if workspace_id column exists
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='portfolios' AND column_name='workspace_id';"))
        exists = result.fetchone()
        
        if not exists:
            print("Adding 'workspace_id' column to 'portfolios' table...")
            conn.execute(text("ALTER TABLE portfolios ADD COLUMN workspace_id VARCHAR(50) DEFAULT 'default';"))
            conn.execute(text("CREATE INDEX ix_portfolios_workspace_id ON portfolios (workspace_id);"))
            conn.commit()
            print("Migration successful.")
        else:
            print("'workspace_id' column already exists.")

if __name__ == "__main__":
    migrate()
