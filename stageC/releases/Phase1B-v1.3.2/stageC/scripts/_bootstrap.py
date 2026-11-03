"""Add the project-local Stage C package to sys.path for standalone scripts."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
