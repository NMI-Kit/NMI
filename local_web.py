"""Loopback-only Flask adapter. AI is disabled unless explicitly enabled at launch."""
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time
from uuid import UUID

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.exceptions import HTTPException

import curriculum
from ai_test import ask_ai, InvalidAIResponse
from local_store import LocalStore, BufferedConversation, StoreError
from claude_provider import ClaudeProvider, ClaudeError, valid_model as valid_claude_model

ROOT = Path(__file__).resolve().parent
COUNTRIES = dict(US="United States", GB="United Kingdom", CA="Canada", DE="Germany",
                 CH="Switzerland", SG="Singapore", AU="Australia", NL="Netherlands",
                 QA="Qatar", AE="United Arab Emirates", IL="Israel")
CURRICULUM_COUNTRY = "IL"  # the only country with curriculum files so far
DEFAULT_MAX_CALLS = 20  # paid attempts per launch of the local server (NMI_MAX_CALLS overrides)
ASSETS = {"tokens.css", "styles.css", "preview.js", "live.js", "live.css"} | {
    f"assets/nmi-mark{suffix}.svg" for suffix in ("", "-light", "-dark", "-white", "-black")}
ERRORS = {
    "claude_locked": ("Claude paid requests are disabled. Only the owner can enable them in the server environment.", "طلبات Claude المدفوعة معطّلة. يمكن لصاحب المشروع فقط تفعيلها من إعدادات الخادم."),
    "claude_key": ("The server's Anthropic credential is missing or invalid. Ask the owner to check it privately.", "بيانات اعتماد Anthropic في الخادم مفقودة أو غير صالحة. اطلب من صاحب المشروع التحقّق منها بشكل خاص."),
    "claude_model": ("The configured Claude model is unavailable or its structured-output support could not be verified. Ask the owner to check the model ID.", "نموذج Claude المحدّد غير متاح أو تعذّر التحقّق من دعمه للردود المنظّمة. اطلب من صاحب المشروع التحقّق من معرّف النموذج."),
    "claude_request": ("Claude rejected the request configuration. Nothing was assessed or added to the conversation.", "رفض Claude إعدادات الطلب. لم يُسجَّل تقييم أو تُضَف رسائل إلى المحادثة."),
    "claude_access": ("This Anthropic account does not permit this request. No other provider was used.", "لا يسمح حساب Anthropic بهذا الطلب. لم تُستخدم خدمة بديلة."),
    "claude_credit": ("Anthropic billing rejected the request. Ask the owner to check the account balance privately.", "رفضت فوترة Anthropic الطلب. اطلب من صاحب المشروع التحقّق من رصيد الحساب بشكل خاص."),
    "claude_limit": ("An Anthropic usage or rate limit was reached. The request was not retried automatically.", "تم بلوغ حدّ للاستخدام أو لمعدّل الطلبات لدى Anthropic. لم يُعَد الطلب تلقائيًا."),
    "claude_unavailable": ("Claude could not complete the reply. Previous conversation and progress are unchanged. No fallback or automatic retry occurred.", "تعذّر على Claude إكمال الرد. المحادثة السابقة والتقدّم محفوظان. لم تُستخدم خدمة بديلة ولم تحدث إعادة محاولة تلقائية."),
    "locked": ("AI is disabled for this launch. Only the owner can enable it.", "الذكاء الاصطناعي معطّل في هذا التشغيل. يمكن لصاحب المشروع فقط تفعيله."),
    "access": ("Open the private local link printed in the server terminal.", "افتح الرابط المحلي الخاص الظاهر في نافذة الخادم."),
    "cookies": ("Allow cookies for 127.0.0.1, then reopen this launch's private link. The session was not claimed.", "اسمح بملفات الارتباط للموقع 127.0.0.1 ثم افتح رابط التشغيل الخاص مجددًا. لم تُحجز الجلسة."),
    "invalid": ("Check the form, country, grade and message, then try again.", "تحقّق من النموذج والبلد والصف والرسالة ثم حاول مجددًا."),
    "profile": ("Create the local test profile first. This server supports one tester only.", "أنشئ ملف الاختبار المحلي أولًا. يدعم هذا الخادم مستخدمًا واحدًا فقط."),
    "profile_incomplete": ("Complete the student profile first: country, grade and units are required before chatting.", "أكمل ملف الطالب أولًا: الدولة والصف والوحدات مطلوبة قبل المحادثة."),
    "timeout": ("The tutor timed out. Nothing was added to history or progress. Provider usage may already have occurred.", "انتهت مهلة الرد. لم يُضَف شيء للسجل أو التقدّم. قد يكون الطلب قد استهلك جزءًا من الاستخدام."),
    "unavailable": ("The AI service could not reply. Your previous conversation and progress are safe.", "تعذّر الحصول على رد من خدمة الذكاء الاصطناعي. محادثتك السابقة وتقدّمك محفوظان."),
    "response": ("No valid tutor reply was received. Nothing was saved or assessed.", "لم يصل رد صالح من المعلّم. لم تُحفظ محادثة أو نتيجة تقييم جديدة."),
    "storage": ("Local storage could not be read or saved. Stop and inspect it; do not delete existing data.", "تعذّرت قراءة التخزين المحلي أو حفظه. توقّف وافحصه دون حذف البيانات السابقة."),
    "busy": ("Another request is running. Wait before sending again.", "يوجد طلب قيد التنفيذ. انتظر قبل إرسال طلب آخر."),
    "limit": ("The local test limit has been reached. No new API call was made.", "وصلت إلى حدّ الاختبار المحلي. لم يُرسَل طلب جديد إلى الخدمة."),
    "conflict": ("This request ID was already used for different content. Reload to reconcile your conversation.", "استُخدم معرّف الطلب لمحتوى مختلف. أعد التحميل لمراجعة المحادثة."),
    "uncertain": ("An earlier request was interrupted. It will not be retried automatically; check your conversation and usage first.", "انقطع طلب سابق ولن يُعاد تلقائيًا. راجع المحادثة والاستخدام أولًا."),
}


class ChatError(Exception):
    def __init__(self, code, status=400):
        self.code, self.status = code, status


def curriculum_options():
    """{subject: {grade: [units]}} read from curriculum/<subject>/grade<N>/<units>units.md."""
    options = {}
    root = Path(curriculum.CURRICULUM_DIR)
    for subject in sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []:
        grades = {}
        for folder in sorted(p for p in subject.iterdir() if p.is_dir() and re.fullmatch(r"grade\d+", p.name)):
            units = sorted(int(m.group(1)) for f in folder.glob("*units.md") if (m := re.fullmatch(r"([345])units\.md", f.name)))
            if units:
                grades[folder.name[5:]] = units
        if grades:
            options[subject.name] = dict(sorted(grades.items(), key=lambda item: int(item[0])))
    return options


def valid_profile(value):
    # "subject", "units" and "target_units" are optional so profiles saved before they existed stay valid.
    if (not isinstance(value, dict) or not {"country", "grade"} <= set(value)
            or not set(value) <= {"country", "grade", "subject", "units", "target_units"}):
        return False
    country, grade = value["country"], value["grade"]
    if not (isinstance(country, str) and country in COUNTRIES and type(grade) is int and grade in {9, 10, 11, 12}):
        return False
    if country != CURRICULUM_COUNTRY:
        return set(value) == {"country", "grade"}
    # Curriculum country: every choice must exist as a file under curriculum/.
    subject = value.get("subject", "math")
    grades = curriculum_options().get(subject) if isinstance(subject, str) else None
    if grades is None or str(grade) not in grades:
        return False
    available = grades[str(grade)]
    if "units" in value and not (type(value["units"]) is int and value["units"] in available):
        return False
    if "target_units" in value:
        # A higher level of the same grade, and only for a student who has a current level.
        target = value["target_units"]
        return ("units" in value and type(target) is int and target in available and target > value["units"])
    return True


def profile_ready(profile):
    """A student may chat only with a profile that has a curriculum: curriculum country, grade and units."""
    return (valid_profile(profile) and profile["country"] == CURRICULUM_COUNTRY and "units" in profile)


def provider_error(error):
    if isinstance(error, ClaudeError):
        return error.code
    if isinstance(error, TimeoutError):
        return "timeout"
    return "unavailable"


def create_app(*, data_path=None, access_token=None, enabled=False, max_calls=1, port=8766,
               claude_factory=ClaudeProvider, claude_model='', allow_claude=False):
    if type(max_calls) is not int or not 1 <= max_calls <= 100:
        raise ValueError('max_calls must be an integer between 1 and 100')
    app = Flask(__name__, static_folder=None)
    app.config.update(SECRET_KEY=secrets.token_hex(32), MAX_CONTENT_LENGTH=20000,
                      SESSION_COOKIE_NAME=f"nmi_local_session_{port}", SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE="Strict", SESSION_COOKIE_SECURE=False,
                      PERMANENT_SESSION_LIFETIME=28800, TRUSTED_HOSTS=["127.0.0.1"])
    token = access_token or secrets.token_urlsafe(32)
    owner = {"claimed": False, "csrf": secrets.token_urlsafe(32), "sid": secrets.token_urlsafe(32)}
    gate = threading.Lock()
    count, last_calls = [0], []
    origin = f"http://127.0.0.1:{port}"
    store = LocalStore(data_path or ROOT / ".local-data" / "tutor.sqlite3")
    app.extensions["nmi_store"] = store
    # SDK debug logs may contain credentials; disable these loggers in every launch/test path.
    for name in ("werkzeug", "anthropic", "anthropic._base_client", "httpx", "httpx2", "httpcore", "httpcore2"):
        logging.getLogger(name).disabled = True

    def fail(code, status=400):
        lang = request.headers.get("X-NMI-Language", "en")
        return jsonify(error=code, message=ERRORS.get(code, ERRORS["unavailable"])[lang == "ar"]), status

    @app.before_request
    def protect():
        if request.host != f"127.0.0.1:{port}" or request.remote_addr not in {"127.0.0.1", "::1"}:
            raise ChatError("access", 403)
        if not request.path.startswith("/api/"):
            return
        if request.headers.get("Sec-Fetch-Site") == "cross-site":
            raise ChatError("access", 403)
        if request.method != "GET":
            if request.headers.get("Origin") != origin or not request.is_json:
                raise ChatError("access", 403)
        if request.path == "/api/session" and request.method == "POST":
            return
        if request.path == '/api/session/preflight' and request.method == 'GET':
            return
        if session.get("sid") != owner["sid"]:
            raise ChatError("access", 401)
        if request.method != "GET" and not secrets.compare_digest(request.headers.get("X-NMI-CSRF", ""), owner["csrf"]):
            raise ChatError("access", 403)

    @app.after_request
    def headers(response):
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"})
        return response

    @app.errorhandler(ChatError)
    def known(error):
        return fail(error.code, error.status)

    @app.errorhandler(ClaudeError)
    def claude_error(error):
        return fail(error.code, 503)

    @app.errorhandler(Exception)
    def unexpected(error):
        # Never log exception strings, bodies, headers, provider payloads or learner text.
        if isinstance(error, HTTPException):
            return fail("invalid", error.code)
        if isinstance(error, (sqlite3.Error, StoreError, OSError)):
            return fail("storage", 503)
        return fail("unavailable", 500)

    @app.get("/")
    def index():
        html = (ROOT / "preview/index.html").read_text(encoding="utf-8")
        html = html.replace("connect-src 'none'", "connect-src 'self'")
        html = html.replace('</head>', '<meta name="nmi-live-server" content="1"></head>')
        # Public launch flags only: no private link or session credentials.
        html = html.replace("</head>", f'<meta name="nmi-inference" content="{int(enabled)}"></head>')
        html = html.replace("</head>", '<link rel="stylesheet" href="live.css"><script src="live.js" defer></script></head>')
        return html

    @app.get("/<path:name>")
    def asset(name):
        if name not in ASSETS:
            raise ChatError("access", 404)
        return send_from_directory(ROOT / "preview", name)

    @app.get('/api/session/preflight')
    def cookie_preflight():
        # Prove the signed HttpOnly cookie survives a round trip before claiming.
        ready = session.get('preflight') is True
        session['preflight'] = True
        return jsonify(cookie_ready=ready)

    @app.post("/api/session")
    def claim():
        body = request.get_json()
        if (not isinstance(body, dict) or not isinstance(body.get("token"), str)
                or not re.fullmatch(r"[A-Za-z0-9_-]{20,100}", body["token"])
                or not secrets.compare_digest(body["token"], token)):
            raise ChatError("access", 403)
        if session.get('preflight') is not True:
            raise ChatError('cookies', 403)
        with gate:
            if owner["claimed"] and session.get("sid") != owner["sid"]:
                raise ChatError("access", 403)
            owner["claimed"] = True
            session["sid"] = owner["sid"]
            session.permanent = True
        return jsonify(csrf=owner["csrf"])

    @app.get("/api/state")
    def state():
        value = store.load()
        if value["profile"] is not None and not valid_profile(value["profile"]):
            raise StoreError()
        # The hidden answer key of an open Bagrut question is for the tutor only: it never leaves the server.
        shown = {name: item for name, item in value.items() if name != "answer_key"}
        return jsonify(**shown, profile_ready=profile_ready(value["profile"]),
                       curriculum=dict(country=CURRICULUM_COUNTRY, options=curriculum_options()),
                       csrf=owner["csrf"], enabled=enabled, remaining=max(0, max_calls-count[0]),
                       claude_enabled=allow_claude, claude_configured=valid_claude_model(claude_model),
                       last_usage=store.usage())

    @app.get('/api/requests/<rid>')
    def receipt(rid):
        try:
            if str(UUID(rid)) != rid:
                raise ValueError()
        except (ValueError, TypeError, AttributeError):
            raise ChatError('invalid')
        row = store.request(rid)
        if row is None:
            return jsonify(status='missing')
        if row[1] == 'done':
            usage = store.usage(rid)
            return jsonify(status='done', reply=row[2], **({'usage': usage} if usage else {}))
        if row[1] == 'pending':
            return jsonify(status='pending')
        code = row[3] if row[3] in ERRORS else 'uncertain'
        return jsonify(status='failed', error=code,
                       message=ERRORS[code][request.headers.get('X-NMI-Language') == 'ar'])

    @app.post("/api/profile")
    def profile():
        value = request.get_json()
        if not valid_profile(value):
            raise ChatError("invalid")
        # A new profile starts the conversation; an edit replaces the profile and keeps the conversation.
        # The next message loads the curriculum of the new profile.
        if not gate.acquire(blocking=False):
            raise ChatError("busy", 409)
        try:
            existing = store.load()["profile"]
            if existing is None:
                store.set_profile(value)
            elif existing != value:
                store.update_profile(value)
        finally:
            gate.release()
        return jsonify(ok=True)

    @app.post("/api/chat")
    def chat():
        body = request.get_json()
        if not isinstance(body, dict) or set(body) != {"request_id", "message", "language", "intent"}:
            raise ChatError("invalid")
        rid, message, lang, intent = (body[k] for k in ("request_id", "message", "language", "intent"))
        if not isinstance(message, str) or not message.strip() or len(message) > 4000 or lang not in ("ar", "en") or intent not in ("question", "answer", "hint", "confusion"):
            raise ChatError("invalid")
        try:
            if not isinstance(rid, str) or str(UUID(rid)) != rid:
                raise ValueError()
        except (ValueError, TypeError, AttributeError):
            raise ChatError("invalid")
        fingerprint = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        if not gate.acquire(blocking=False):
            raise ChatError("busy", 409)
        try:
            previous = store.request(rid)
            if previous:
                if previous[0] != fingerprint:
                    raise ChatError("conflict", 409)
                if previous[1] == "done":
                    usage = store.usage(rid)
                    return jsonify(reply=previous[2], replayed=True, **({'usage': usage} if usage else {}))
                raise ChatError(previous[3] or "uncertain", 409)
            if not enabled:
                raise ChatError("locked", 503)
            if not allow_claude:
                raise ChatError('claude_locked', 503)
            if not valid_claude_model(claude_model):
                raise ChatError('claude_model', 503)
            current = store.load()
            if current["profile"] is None or not valid_profile(current["profile"]):
                raise ChatError("profile", 409)
            if not profile_ready(current["profile"]):
                raise ChatError("profile_incomplete", 409)
            last_calls[:] = [v for v in last_calls if time.monotonic()-v < 60]
            if count[0] >= max_calls or len(last_calls) >= 6 or len(current["history"]) >= 200:
                raise ChatError("limit", 429)
            client = claude_factory(claude_model)
            store.begin(rid, fingerprint)
            count[0] += 1
            last_calls.append(time.monotonic())
            buffered = BufferedConversation(current)
            p = current["profile"]
            try:
                reply = ask_ai("Learner", str(p["grade"]), COUNTRIES[p["country"]], lang, message,
                               storage=buffered, ai_client=client, model=claude_model, web_policy=True, intent=intent,
                               subject=p.get("subject", "math"), units=p.get("units"),
                               target_units=p.get("target_units"))
                usage = getattr(client, 'usage', None)
                store.commit(rid, buffered.state, reply, usage=usage)
            except Exception as error:
                code = ("response" if isinstance(error, InvalidAIResponse) else
                        "storage" if isinstance(error, (sqlite3.Error, StoreError, OSError)) and not isinstance(error, TimeoutError) else provider_error(error))
                usage = getattr(client, 'usage', None)
                store.fail(rid, code, usage=usage)
                raise ChatError(code, 503)
            finally:
                try:
                    client.close()
                except Exception:
                    pass  # Closing the transport must not turn a committed reply into a failure.
            return jsonify(reply=reply, replayed=False, **({'usage': usage} if usage else {}))
        finally:
            gate.release()

    return app


def main():
    # Single process lock prevents two local servers sharing the one-tester store.
    import msvcrt
    directory = ROOT / ".local-data"
    directory.mkdir(exist_ok=True)
    with (directory / "server.lock").open("a+b") as lock:
        lock.seek(0, 2)
        if lock.tell() == 0:
            lock.write(b"0"); lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise SystemExit("NMI local server is already running. Stop that process first.")
        token = secrets.token_urlsafe(32)
        claude_model = os.environ.get('NMI_CLAUDE_MODEL', '')
        allow_claude = os.environ.get('NMI_ENABLE_ANTHROPIC_PAID') == '1'
        try:
            max_calls = int(os.environ.get('NMI_MAX_CALLS', str(DEFAULT_MAX_CALLS)))
            if not 1 <= max_calls <= 100:
                raise ValueError()
        except ValueError:
            raise SystemExit('NMI_MAX_CALLS must be an integer from 1 through 100.')
        enabled = os.environ.get("NMI_ENABLE_AI") == "1"
        app = create_app(access_token=token, enabled=enabled, claude_model=claude_model,
                         allow_claude=allow_claude, max_calls=max_calls)
        logging.getLogger("werkzeug").disabled = True
        print("Local single-tester NMI. AI " + (f"ENABLED ({max_calls} attempt(s) per launch)" if enabled else "DISABLED"), flush=True)
        print('Anthropic paid inference ' + ('ENABLED' if allow_claude else 'DISABLED') +
              '. Model ' + ('configured' if valid_claude_model(claude_model) else 'NOT CONFIGURED'), flush=True)
        print(f"Open privately: http://127.0.0.1:8766/#local-access={token}", flush=True)
        app.run(host="127.0.0.1", port=8766, debug=False, use_reloader=False, load_dotenv=False)


if __name__ == "__main__":
    main()
