"""Local ChatGPT conversations. OAuth and inference require explicit owner actions."""
import argparse
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
import secrets
import sys
import threading
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chatgpt_auth import ChatGPTAuth, AuthError
from local_web import create_app, ChatError


def forbidden_api():
    raise RuntimeError('Paid API disabled in the ChatGPT launcher')


def build_conversation_app(directory, capability, *, max_calls=20):
    """Reuse only this launcher's store; never import CLI or legacy website data."""
    directory = Path(directory)
    auth = ChatGPTAuth(directory / 'registration.json',
                       'http://127.0.0.1:8766/auth/callback')
    return create_app(data_path=directory / 'tutor.sqlite3', access_token=capability,
                      enabled=False, signin_enabled=True, chatgpt_auth=auth,
                      allow_api=False, client_factory=forbidden_api, max_calls=max_calls)


def build_test_app(directory, capability):
    """Optional one-request test mode, without any restriction on question content."""
    directory = Path(directory)
    path = directory / 'synthetic.sqlite3'
    if path.exists():
        raise ValueError('Use a fresh test directory; existing data is preserved.')
    auth = ChatGPTAuth(ROOT / '.local-data' / 'synthetic-chatgpt' / 'registration.json',
                       'http://127.0.0.1:8766/auth/callback')
    app = create_app(data_path=path, access_token=capability, enabled=False,
                     signin_enabled=True, chatgpt_auth=auth, allow_api=False,
                     client_factory=forbidden_api, max_calls=1)
    app.extensions['nmi_store'].set_profile({'country': 'US', 'grade': 10})
    return app


def report_saved_state(app):
    """Owner console counts only; never print transcript, profile or credentials."""
    store = app.extensions['nmi_store']
    value = store.load()
    with closing(store.connect()) as db:
        receipts = dict(db.execute('SELECT status,COUNT(*) FROM requests GROUP BY status'))
    return {'history_messages': len(value['history']), 'attempts': len(value['attempts']),
            'receipts': receipts}


def owner_command(app, line):
    """No automatic authorization, inference, retry or billing fallback."""
    command, _, argument = line.strip().partition(' ')
    control = app.extensions['nmi_control']
    if command == 'status':
        return {'connection': control.status(), 'saved': report_saved_state(app)}
    if command == 'models':
        return {'authorized_models': [item['slug'] for item in control.models()]}
    if command in {'enable', 'arm'} and argument:
        return control.arm_chatgpt(argument.strip())
    if command == 'quit':
        return None
    return 'Commands: status | models | enable AUTHORIZED_MODEL_SLUG | quit'


@contextmanager
def exclusive_store(directory):
    """Prevent two Windows processes from opening this same single-user store."""
    import msvcrt
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'server.lock').open('a+b') as lock:
        lock.seek(0, 2)
        if lock.tell() == 0:
            lock.write(b'0')
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise SystemExit('This NMI conversation server is already running. Stop it first.')
        try:
            yield
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


def parse_options(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-calls', type=int, default=None,
                        help='Owner-set inference attempts per launch, 1-100 (default: 20).')
    parser.add_argument('--acceptance', action='store_true',
                        help='Fresh fictional data, one attempt; any Arabic or English question.')
    args = parser.parse_args(argv)
    if args.max_calls is not None and not 1 <= args.max_calls <= 100:
        parser.error('--max-calls must be between 1 and 100')
    if args.acceptance and args.max_calls not in (None, 1):
        parser.error('--acceptance permits one attempt only')
    args.max_calls = 1 if args.acceptance else (args.max_calls or 20)
    return args


def main(argv=None):
    from werkzeug.serving import make_server
    args = parse_options(argv)
    if not sys.stdin.isatty():
        raise SystemExit('Start this launcher in your own interactive PowerShell terminal.')
    directory = (ROOT / '.cache' / 'live-acceptance' / (
        datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid4().hex[:8])
        if args.acceptance else ROOT / '.local-data' / 'chatgpt-conversations')
    with exclusive_store(directory):
        # Bind before opening conversation data; start serving only after app setup.
        server = make_server('127.0.0.1', 8766, None, threaded=True)
        thread = None
        try:
            capability = secrets.token_urlsafe(32)
            app = (build_test_app(directory, capability) if args.acceptance else
                   build_conversation_app(directory, capability, max_calls=args.max_calls))
            server.app = app
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            print('NMI ChatGPT plan: sign-in ON; inference OFF; paid API OFF.')
            print('Mode: ' + ('one-request synthetic acceptance' if args.acceptance else 'persistent local conversations'))
            print(f'Owner-set allowance after enable: {args.max_calls} attempt(s) this launch.')
            print('Local records: ' + str(directory.relative_to(ROOT)))
            print('Open privately in one Chrome profile; do not share or screenshot this URL:')
            print(f'http://127.0.0.1:8766/#local-access={capability}', flush=True)
            print('In Tutor connection, save the local profile if requested and authorize ChatGPT personally.')
            print('Then run models here and enable AUTHORIZED_MODEL_SLUG. No request is sent by enabling.')
            print('Refresh NMI connection status, review consent and ask your own Arabic or English question.')
            print('Commands: status | models | enable AUTHORIZED_MODEL_SLUG | quit', flush=True)
            while True:
                try:
                    result = owner_command(app, input('NMI owner> '))
                    if result is None:
                        break
                    print(result, flush=True)
                except (AuthError, ChatError) as error:
                    print('Action stopped. Safe error code: ' + error.code, flush=True)
                except (EOFError, KeyboardInterrupt):
                    break
                except Exception:
                    print('Action stopped. Local configuration/storage failure; details suppressed.', flush=True)
        finally:
            if thread is not None:
                server.shutdown()
                thread.join(timeout=5)
            server.server_close()
            print('Server stopped. Local records preserved. No automatic remote revocation.', flush=True)


if __name__ == '__main__':
    main()
