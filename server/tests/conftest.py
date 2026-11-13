import sys
from pathlib import Path

# Add repo root to sys.path so 'server' is recognized as a package
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
