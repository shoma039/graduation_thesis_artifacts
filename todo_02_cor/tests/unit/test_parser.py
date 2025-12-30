import sys
from pathlib import Path

# Ensure project root is importable
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.services import parser


def test_parse_tomorrow():
    dt = parser.parse_natural_date("明日")
    assert dt is not None
