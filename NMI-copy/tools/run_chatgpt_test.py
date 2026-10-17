"""Compatibility entry point for isolated, one-request acceptance (any question)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.run_chatgpt import build_test_app, owner_command, report_saved_state, main


if __name__ == '__main__':
    main(['--acceptance', *sys.argv[1:]])
