"""Owner-launched local Claude chat; both inference gates default OFF."""
import argparse
from contextlib import contextmanager
from pathlib import Path
import logging
import os
import secrets
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from claude_provider import check_model, ClaudeError
from local_web import create_app, DEFAULT_MAX_CALLS


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


def build_app(directory, capability, *, acceptance=False, max_calls=DEFAULT_MAX_CALLS, environ=None):
    settings = os.environ if environ is None else environ
    path = Path(directory)/('synthetic.sqlite3' if acceptance else 'tutor.sqlite3')
    if acceptance and path.exists():
        raise ValueError('Acceptance requires a fresh directory; existing data is preserved.')
    app = create_app(data_path=path, access_token=capability,
        claude_model=settings.get('NMI_CLAUDE_MODEL',''),
        enabled=settings.get('NMI_ENABLE_AI') == '1',
        allow_claude=settings.get('NMI_ENABLE_ANTHROPIC_PAID') == '1',
        max_calls=1 if acceptance else max_calls)
    if acceptance:
        app.extensions['nmi_store'].set_profile({'country':'IL','grade':10,'subject':'math','units':4})
    return app


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acceptance',action='store_true',help='Fresh synthetic profile and storage, one attempt.')
    parser.add_argument('--max-calls',type=int,default=DEFAULT_MAX_CALLS,help='Attempts per launch, 1-100; default '+str(DEFAULT_MAX_CALLS)+'.')
    parser.add_argument('--check-model',action='store_true',help='Explicit account model metadata GET only; no inference.')
    args = parser.parse_args(argv)
    if args.acceptance:
        args.max_calls = 1  # acceptance is exactly one attempt, whatever the default is
    if not 1 <= args.max_calls <= 100:
        parser.error('Use 1-100 attempts.')
    return args


def main(argv=None):
    args = parse_args(argv)
    if args.check_model:
        try:
            result = check_model(os.environ.get('NMI_CLAUDE_MODEL',''))
            print('Account model verified: '+result['model']+'. Structured outputs supported. No inference sent.')
        except ClaudeError as error:
            raise SystemExit('Model check failed. Safe code: '+error.code) from None
        return
    from werkzeug.serving import make_server
    directory = (ROOT/'.cache/claude-acceptance'/uuid4().hex if args.acceptance
                 else ROOT/'.local-data/claude-conversations')
    logging.getLogger('werkzeug').disabled = True
    with exclusive_store(directory):
        # Bind first: a conflicting server must not trigger a storage migration.
        server = make_server('127.0.0.1',8766,None,threaded=True)
        try:
            capability = secrets.token_urlsafe(32)
            server.app = build_app(directory,capability,acceptance=args.acceptance,max_calls=args.max_calls)
            armed = os.environ.get('NMI_ENABLE_AI') == '1' and os.environ.get('NMI_ENABLE_ANTHROPIC_PAID') == '1'
            print('NMI Claude: paid inference '+('ENABLED' if armed else 'DISABLED')+'.')
            print('Attempt limit: '+str(args.max_calls)+'. No automatic retries or provider fallback.')
            print('Records: '+str(directory.relative_to(ROOT)))
            print('Open privately in one Chrome profile; never share or screenshot the following local link:')
            print(f'http://127.0.0.1:8766/#local-access={capability}',flush=True)
            print('Ctrl+C stops this server. No API request is sent on startup.',flush=True)
            try: server.serve_forever()
            except KeyboardInterrupt: pass
        finally:
            server.server_close()


if __name__ == '__main__': main()
