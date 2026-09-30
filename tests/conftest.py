import os
import sys
import tempfile
from pathlib import Path

# Make the repository root importable (preprocessing/, pdf_parser/, ...)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Keep test logs and uploads out of the project folder
_TMP = Path(tempfile.gettempdir()) / "talentsync-tests"
os.environ.setdefault("LOG_DIR", str(_TMP / "logs"))
os.environ.setdefault("UPLOAD_DIR", str(_TMP / "uploads"))
