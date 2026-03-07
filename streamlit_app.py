import sys
import os

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
from app.main import main

if __name__ == "__main__":
    main()
