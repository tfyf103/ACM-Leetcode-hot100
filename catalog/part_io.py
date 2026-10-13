"""Original exercises for common ACM input and output protocols."""
import json
from pathlib import Path


PROBLEMS = json.loads(Path(__file__).with_name("io_basics.json").read_text(encoding="utf-8"))
CHECKERS = {}
