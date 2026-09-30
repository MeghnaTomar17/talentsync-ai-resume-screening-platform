import sys
from pathlib import Path

# Make the repository root importable (preprocessing/, pdf_parser/, ...)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
