import sys

from pathlib import Path

from app import App

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # project root (for config.py)
import config

if __name__ == "__main__":
    # TODO: load config better somehow
    app = App(config=config)