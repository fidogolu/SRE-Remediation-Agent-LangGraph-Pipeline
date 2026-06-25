# conftest.py
"""Project-level pytest configuration."""
import sys
from pathlib import Path

# Add project root to Python path
root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
