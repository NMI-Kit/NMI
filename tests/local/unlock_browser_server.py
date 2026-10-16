"""Sign-in-ready fixture; network, authorization and inference are forbidden."""
from pathlib import Path
import socket
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from local_web import create_app
from chatgpt_auth import ChatGPTAuth


if __name__ == '__main__':
    base = ROOT / '.cache/unlock-browser'
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as temporary:
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('No external network')), \
             patch.object(ChatGPTAuth, 'start', side_effect=AssertionError('No authorization')):
            app = create_app(data_path=Path(temporary)/'state.sqlite3',
                             access_token='synthetic-local-unlock-not-a-real-secret',
                             signin_enabled=True, enabled=False, port=8769)
            app.run(host='127.0.0.1', port=8769, debug=False, use_reloader=False, load_dotenv=False)
