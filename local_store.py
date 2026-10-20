"""One local tester, one conversation; never reads the CLI JSON stores."""
import copy
import json
import sqlite3
from contextlib import closing
from pathlib import Path


class StoreError(Exception):
    pass


class BufferedConversation:
    def __init__(self, state):
        self.state = copy.deepcopy(state)

    def load_history(self):
        return copy.deepcopy(self.state["history"][-20:])

    def load_progress(self):
        return {"attempts": copy.deepcopy(self.state["attempts"][-100:])}

    def record_attempt(self, subject, topic, skill, correct, hint_used, mistake_type):
        self.state["attempts"].append(dict(subject=subject, topic=topic, skill=skill,
                                          correct=correct, hint_used=hint_used,
                                          mistake_type=mistake_type))

    def save_history(self, history):
        # ask_ai sees bounded context; keep the full prior local conversation.
        self.state["history"].extend(copy.deepcopy(history[-2:]))


class LocalStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, status TEXT NOT NULL, reply TEXT, error TEXT)")
            # Additive, non-personal usage ledger; existing state/receipts are preserved.
            db.execute("CREATE TABLE IF NOT EXISTS request_usage (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            # A process interruption must never silently repeat a potentially paid call.
            db.execute("UPDATE requests SET status='failed', error='uncertain' WHERE status='pending'")

    def connect(self):
        db = sqlite3.connect(self.path, timeout=2)
        db.execute("PRAGMA synchronous=FULL")
        return db

    def load(self):
        with closing(self.connect()) as db:
            row = db.execute("SELECT payload FROM state WHERE id=1").fetchone()
        if row is None:
            return {"profile": None, "history": [], "attempts": []}
        try:
            state = json.loads(row[0])
            assert set(state) == {"profile", "history", "attempts"}
            assert isinstance(state["profile"], dict)
            assert isinstance(state["history"], list) and len(state["history"]) <= 200
            assert isinstance(state["attempts"], list) and len(state["attempts"]) <= 100
            for message in state["history"]:
                assert set(message) == {"role", "content"}
                assert message["role"] in {"user", "assistant"}
                assert isinstance(message["content"], str) and 0 < len(message["content"]) <= 16000
            for attempt in state["attempts"]:
                assert attempt["subject"] in {"mathematics", "physics", "chemistry"}
                assert all(isinstance(attempt[k], str) and attempt[k].strip() for k in ("topic", "skill"))
                assert type(attempt["correct"]) is bool and type(attempt["hint_used"]) is bool
            return state
        except (ValueError, TypeError, KeyError, AssertionError) as error:
            raise StoreError() from error

    def set_profile(self, profile):
        state = {"profile": profile, "history": [], "attempts": []}
        with closing(self.connect()) as db, db:
            db.execute("INSERT INTO state(id,payload) VALUES(1,?)", (json.dumps(state),))

    def update_profile(self, profile):
        """Replace the profile only. History and attempts are kept; unreadable data is never overwritten."""
        with closing(self.connect()) as db, db:
            row = db.execute("SELECT payload FROM state WHERE id=1").fetchone()
            if row is None:
                state = {"profile": profile, "history": [], "attempts": []}
                db.execute("INSERT INTO state(id,payload) VALUES(1,?)", (json.dumps(state, ensure_ascii=False),))
                return
            try:
                state = json.loads(row[0])
                assert isinstance(state, dict) and set(state) == {"profile", "history", "attempts"}
            except (ValueError, TypeError, AssertionError) as error:
                raise StoreError() from error
            state["profile"] = profile
            db.execute("UPDATE state SET payload=? WHERE id=1", (json.dumps(state, ensure_ascii=False),))

    def request(self, request_id):
        with closing(self.connect()) as db:
            row = db.execute("SELECT fingerprint,status,reply,error FROM requests WHERE id=?", (request_id,)).fetchone()
        return row

    def begin(self, request_id, fingerprint):
        with closing(self.connect()) as db, db:
            db.execute("INSERT INTO requests(id,fingerprint,status) VALUES(?,?,'pending')", (request_id, fingerprint))

    def _save_usage(self, db, request_id, usage):
        if usage is not None:
            fields = {'input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'}
            if (not isinstance(usage, dict) or set(usage) != fields | {'provider', 'complete'}
                    or usage['provider'] != 'claude' or type(usage['complete']) is not bool
                    or any(usage[k] is not None and (type(usage[k]) is not int or usage[k] < 0) for k in fields)):
                raise StoreError()
            db.execute('INSERT OR REPLACE INTO request_usage(id,payload) VALUES(?,?)',
                       (request_id, json.dumps(usage)))

    def usage(self, request_id=None):
        with closing(self.connect()) as db:
            row = (db.execute('SELECT payload FROM request_usage WHERE id=?', (request_id,)).fetchone()
                   if request_id else db.execute('SELECT payload FROM request_usage ORDER BY rowid DESC LIMIT 1').fetchone())
        if row is None:
            return None
        try:
            value = json.loads(row[0])
            fields = {'input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'}
            if (not isinstance(value, dict) or set(value) != fields | {'provider', 'complete'}
                    or value['provider'] != 'claude' or type(value['complete']) is not bool
                    or any(value[k] is not None and (type(value[k]) is not int or value[k] < 0) for k in fields)):
                raise ValueError()
            return value
        except (ValueError, TypeError):
            raise StoreError() from None

    def fail(self, request_id, code, *, usage=None):
        with closing(self.connect()) as db, db:
            db.execute("UPDATE requests SET status='failed', error=? WHERE id=?", (code, request_id))
            self._save_usage(db, request_id, usage)

    def commit(self, request_id, state, reply, *, usage=None):
        payload = json.dumps(state, ensure_ascii=False)
        if len(payload) > 1500000:
            raise StoreError()
        with closing(self.connect()) as db, db:
            db.execute("UPDATE state SET payload=? WHERE id=1", (payload,))
            db.execute("UPDATE requests SET status='done', reply=? WHERE id=?", (reply, request_id))
            self._save_usage(db, request_id, usage)
