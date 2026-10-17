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

from flask import Flask, jsonify, request, send_from_directory, session, redirect
from werkzeug.exceptions import HTTPException

from ai_test import ask_ai, InvalidAIResponse
from local_store import LocalStore, BufferedConversation, StoreError
from chatgpt_auth import ChatGPTAuth, AuthError
from chatgpt_provider import ChatGPTProvider, PlanError
from claude_provider import ClaudeProvider, ClaudeError, valid_model as valid_claude_model

ROOT = Path(__file__).resolve().parent
COUNTRIES = dict(US="United States", GB="United Kingdom", CA="Canada", DE="Germany",
                 CH="Switzerland", SG="Singapore", AU="Australia", NL="Netherlands",
                 QA="Qatar", AE="United Arab Emirates")
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
    "oauth": ("ChatGPT sign-in could not be verified. Start sign-in again; no tutoring request was sent.", "تعذّر التحقّق من تسجيل الدخول إلى ChatGPT. ابدأ تسجيل الدخول مجددًا؛ لم يُرسل طلب تعليمي."),
    "signin": ("Sign in to ChatGPT again before sending. No switch to API billing will occur.", "سجّل الدخول إلى ChatGPT مجددًا قبل الإرسال. لن يحدث تحويل إلى فوترة API."),
    "consent": ("ChatGPT plan permission was not granted. Continue with ChatGPT to review consent.", "لم تُمنح صلاحية استخدام خطة ChatGPT. تابع عبر ChatGPT لمراجعة الموافقة."),
    "account": ("This local setup is bound to a different ChatGPT account. Existing records were not reassigned.", "هذا الإعداد المحلي مرتبط بحساب ChatGPT آخر. لم تُنقل السجلات السابقة."),
    "revocation": ("Signed out locally, but remote revocation was not confirmed. Disconnect NMI in ChatGPT settings.", "تم تسجيل الخروج محليًا، لكن إلغاء الصلاحية عن بُعد لم يُؤكّد. افصل NMI في إعدادات ChatGPT."),
    "plan_limit": ("A ChatGPT plan or app limit was reached. Review ChatGPT usage settings; no API billing fallback occurred.", "تم بلوغ حدّ لخطة ChatGPT أو للتطبيق. راجع إعدادات الاستخدام؛ لم يحدث تحويل إلى فوترة API."),
    "plan_eligibility": ("This account, workspace or region cannot use this ChatGPT plan request. Check access in ChatGPT.", "لا يمكن لهذا الحساب أو مساحة العمل أو المنطقة استخدام طلب خطة ChatGPT هذا. راجع صلاحيات الوصول في ChatGPT."),
    "plan_unavailable": ("ChatGPT plan usage is temporarily unavailable. History and progress are unchanged. Review usage before retrying.", "استخدام خطة ChatGPT غير متاح مؤقتًا. لم يتغيّر السجل أو التقدّم. راجع الاستخدام قبل المحاولة مجددًا."),
    "locked": ("Real AI is disabled. Follow the local activation guide.", "الذكاء الاصطناعي الحقيقي معطّل. اتبع دليل التفعيل المحلي."),
    "access": ("Open the private local link printed in the server terminal.", "افتح الرابط المحلي الخاص الظاهر في نافذة الخادم."),
    "cookies": ("Allow cookies for 127.0.0.1, then reopen this launch's private link. The session was not claimed.", "اسمح بملفات الارتباط للموقع 127.0.0.1 ثم افتح رابط التشغيل الخاص مجددًا. لم تُحجز الجلسة."),
    "invalid": ("Check the form, country, grade and message, then try again.", "تحقّق من النموذج والبلد والصف والرسالة ثم حاول مجددًا."),
    "profile": ("Create the local test profile first. This server supports one tester only.", "أنشئ ملف الاختبار المحلي أولًا. يدعم هذا الخادم مستخدمًا واحدًا فقط."),
    "key": ("The server API key is missing or invalid. Check it in the server terminal, never here.", "مفتاح الخادم مفقود أو غير صالح. تحقّق منه في نافذة الخادم، وليس هنا."),
    "model": ("The tutor model is not configured or is unavailable. The project owner must check the server model setting against this account's authorized models.", "نموذج المعلّم غير مُعدّ أو غير متاح. على صاحب المشروع التحقّق من إعداد النموذج في الخادم ومن النماذج المسموح بها للحساب."),
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


def valid_profile(value):
    return (isinstance(value, dict) and set(value) == {"country", "grade"}
            and isinstance(value["country"], str) and value["country"] in COUNTRIES
            and type(value["grade"]) is int and value["grade"] in {9, 10, 11, 12})


def real_client():
    # Only invoked after the launch gate and a user-initiated valid send.
    from openai import OpenAI
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise ChatError("key", 503)
    # Pin the official endpoint; do not inherit an arbitrary OPENAI_BASE_URL.
    return OpenAI(api_key=key, base_url="https://api.openai.com/v1", timeout=35, max_retries=0)


def provider_error(error):
    import openai
    if isinstance(error, (AuthError, PlanError, ClaudeError)):
        return error.code
    if isinstance(error, (openai.APITimeoutError, TimeoutError)):
        return "timeout"
    if isinstance(error, openai.AuthenticationError):
        return "key"
    if isinstance(error, (openai.NotFoundError, openai.PermissionDeniedError, openai.BadRequestError)):
        return "model"
    return "unavailable"


def create_app(*, data_path=None, access_token=None, enabled=False, model="", max_calls=1,
               client_factory=real_client, port=8766, signin_enabled=False, chatgpt_auth=None,
               plan_factory=ChatGPTProvider, plan_model='', allow_api=False,
               provider=None, claude_factory=ClaudeProvider, claude_model='', allow_claude=False):
    if type(max_calls) is not int or not 1 <= max_calls <= 100:
        raise ValueError('max_calls must be an integer between 1 and 100')
    if provider not in (None, 'api', 'chatgpt', 'claude'):
        raise ValueError('Unknown NMI provider')
    claude_selected = provider == 'claude'
    if claude_selected:
        # Claude launch cannot use, authorize or fall back to either OpenAI route.
        allow_api, signin_enabled = False, False
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
    auth = chatgpt_auth or ChatGPTAuth(store.path.with_suffix(".chatgpt-registration.json"), origin + "/auth/callback")
    app.extensions["nmi_chatgpt"] = auth
    mode = [provider or ("chatgpt" if signin_enabled else "api")]
    runtime = {"enabled": enabled, "model": plan_model, "armed": False}

    class DeveloperControl:
        """In-process owner terminal controls. Never exposed as HTTP configuration."""
        def status(self):
            with gate:
                connection = auth.public_state()
                return dict(connected=connection['connected'], sharing=connection['sharing'],
                            enabled=runtime['enabled'], remaining=max(0, max_calls-count[0]),
                            model=runtime['model'], armed=runtime['armed'],
                            signin_enabled=signin_enabled, api_enabled=allow_api)

        def models(self):
            with gate:
                if not signin_enabled or allow_api:
                    raise ChatError('locked', 403)
                return auth.load_models()

        def arm_chatgpt(self, selected_model):
            """Enable the owner-configured session budget, without restricting prompts."""
            with gate:
                if (claude_selected or not signin_enabled or allow_api or count[0]
                        or runtime['armed'] or runtime['enabled']):
                    raise ChatError('locked', 403)
                if (not isinstance(selected_model, str)
                        or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}', selected_model)):
                    raise ChatError('model', 400)
                if not auth.public_state()['sharing']:
                    raise ChatError('consent', 403)
                auth.load_models()
                auth.select_model(selected_model)
                runtime.update(enabled=True, model=selected_model, armed=True)
                mode[0] = 'chatgpt'
                return dict(enabled=True, remaining=max_calls)

    app.extensions['nmi_control'] = DeveloperControl()
    # Callback URLs contain authorization codes. SDK debug logs may contain credentials.
    # Disable these loggers in every supported launch/test path, not just __main__.
    for name in ("werkzeug", "openai", "openai._base_client", "anthropic", "anthropic._base_client", "httpx", "httpx2", "httpcore", "httpcore2"):
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

    @app.errorhandler(AuthError)
    @app.errorhandler(ClaudeError)
    def auth_error(error):
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
        # Public launch flags only: no private link, session or OAuth credentials.
        html = html.replace("</head>", f'<meta name="nmi-chatgpt-signin" content="{int(signin_enabled)}">'
                            f'<meta name="nmi-inference" content="{int(runtime["enabled"])}"></head>')
        html = html.replace('</head>', f'<meta name="nmi-provider" content="{mode[0]}"></head>')
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
        connection = auth.public_state()
        public_connection = {k:connection[k] for k in ('connected','sharing','error')}
        public_connection['ready'] = bool(runtime['model'] and auth.selected_model == runtime['model'] and connection['sharing'])
        return jsonify(**value, csrf=owner["csrf"], enabled=runtime['enabled'], remaining=max(0, max_calls-count[0]),
                       claude_enabled=claude_selected and allow_claude,
                       claude_configured=valid_claude_model(claude_model), provider_locked=claude_selected,
                       last_usage=store.usage(),
                       provider=mode[0], api_enabled=allow_api, signin_enabled=signin_enabled, chatgpt=public_connection,
                       chatgpt_message=ERRORS.get(auth.last_error, ("", ""))[request.headers.get("X-NMI-Language") == "ar"])

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

    def exclusive(action):
        if not gate.acquire(blocking=False):
            raise ChatError("busy", 409)
        try:
            return action()
        finally:
            gate.release()

    @app.post("/api/provider")
    def choose_provider():
        body = request.get_json()
        if not isinstance(body, dict) or set(body) != {"provider"} or body["provider"] not in ("api", "chatgpt", "claude"):
            raise ChatError("invalid")
        def choose():
            if claude_selected or body['provider'] == 'claude':
                raise ChatError('access',403)  # Claude is chosen only in server configuration.
            if body['provider']=='api' and not allow_api:
                raise ChatError('locked',403)
            mode[0] = body["provider"]
            return jsonify(ok=True)
        return exclusive(choose)

    @app.post("/api/chatgpt/start")
    def start_signin():
        if not signin_enabled:
            raise ChatError("locked", 503)
        return exclusive(lambda: jsonify(url=auth.start()))

    @app.get("/auth/callback")
    def oauth_callback():
        # SameSite=Strict cookies do not arrive on this cross-site navigation.
        # Only this route uses one-use OAuth state instead of the app cookie/CSRF.
        if not signin_enabled or not owner["claimed"] or any(len(request.args.getlist(k)) != 1 for k in request.args) or len(request.query_string) > 12000:
            raise ChatError("access", 403)
        def finish():
            try:
                auth.finish(request.args.to_dict())
            except AuthError as error:
                auth.last_error = error.code
            return redirect("/", code=303)
        return exclusive(finish)

    @app.post("/api/chatgpt/models")
    def load_models():
        if not signin_enabled:
            raise ChatError("locked", 503)
        def configure():
            models = auth.load_models()
            # Slugs are validated non-secret identifiers; credentials never leave Python.
            print('NMI account-authorized model slugs: ' + ', '.join(m['slug'] for m in models), flush=True)
            if not runtime['model']:
                raise ChatError('model',503)
            auth.select_model(runtime['model'])
            return jsonify(ready=True)
        return exclusive(configure)

    @app.post("/api/chatgpt/model")
    def choose_model():
        # Browser sessions are student sessions, not developer configuration.
        raise ChatError('access', 403)

    @app.post("/api/chatgpt/signout")
    def signout():
        return exclusive(lambda: jsonify(revoked=auth.sign_out()))

    @app.post("/api/profile")
    def profile():
        value = request.get_json()
        if not valid_profile(value):
            raise ChatError("invalid")
        with gate:
            existing = store.load()["profile"]
            if existing is not None and existing != value:
                raise ChatError("profile", 409)
            if existing is None:
                store.set_profile(value)
        return jsonify(ok=True)

    @app.post("/api/chat")
    def chat():
        body = request.get_json()
        if not isinstance(body, dict) or set(body) not in ({"request_id", "message", "language", "intent"}, {"request_id", "message", "language", "intent", "provider"}):
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
            if body.get("provider", "api") != mode[0]:
                raise ChatError("conflict", 409)
            previous = store.request(rid)
            if previous:
                if previous[0] != fingerprint:
                    raise ChatError("conflict", 409)
                if previous[1] == "done":
                    usage = store.usage(rid)
                    return jsonify(reply=previous[2], replayed=True, **({'usage': usage} if usage else {}))
                raise ChatError(previous[3] or "uncertain", 409)
            if not runtime['enabled']:
                raise ChatError("locked", 503)
            if mode[0] == 'claude' and not allow_claude:
                raise ChatError('claude_locked', 503)
            if mode[0] == 'api' and not allow_api:
                raise ChatError('locked',403)
            active_model = claude_model if mode[0] == 'claude' else model if mode[0] == "api" else runtime['model']
            if mode[0] == 'claude' and not valid_claude_model(active_model):
                raise ChatError('claude_model', 503)
            if not active_model or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", active_model):
                raise ChatError("model", 503)
            current = store.load()
            if current["profile"] is None or not valid_profile(current["profile"]):
                raise ChatError("profile", 409)
            last_calls[:] = [v for v in last_calls if time.monotonic()-v < 60]
            if count[0] >= max_calls or len(last_calls) >= 6 or len(current["history"]) >= 200:
                raise ChatError("limit", 429)
            if mode[0] == "chatgpt":
                if not signin_enabled:
                    raise ChatError("locked", 503)
                # Recheck the current account catalog; never accept an arbitrary browser model.
                auth.load_models()
                auth.select_model(active_model)
                client = plan_factory(auth.access_token(), active_model)
            elif mode[0] == 'api':
                client = client_factory()
            elif mode[0] == 'claude':
                client = claude_factory(active_model)
            else:
                raise ChatError('invalid')
            store.begin(rid, fingerprint)
            count[0] += 1
            last_calls.append(time.monotonic())
            buffered = BufferedConversation(current)
            p = current["profile"]
            try:
                reply = ask_ai("Learner", str(p["grade"]), COUNTRIES[p["country"]], lang, message,
                               storage=buffered, ai_client=client, model=active_model, web_policy=True, intent=intent)
                usage = getattr(client, 'usage', None) if mode[0] == 'claude' else None
                store.commit(rid, buffered.state, reply, usage=usage)
            except Exception as error:
                code = ("response" if isinstance(error, InvalidAIResponse) else
                        "storage" if isinstance(error, (sqlite3.Error, StoreError, OSError)) and not isinstance(error, TimeoutError) else provider_error(error))
                usage = getattr(client, 'usage', None) if mode[0] == 'claude' else None
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
        provider = os.environ.get('NMI_AI_PROVIDER') or None
        claude_model = os.environ.get('NMI_CLAUDE_MODEL', '')
        allow_claude = os.environ.get('NMI_ENABLE_ANTHROPIC_PAID') == '1'
        try:
            max_calls = int(os.environ.get('NMI_MAX_CALLS', '1'))
            if not 1 <= max_calls <= 100:
                raise ValueError()
        except ValueError:
            raise SystemExit('NMI_MAX_CALLS must be an integer from 1 through 100.')
        enabled = os.environ.get("NMI_ENABLE_AI") == "1"
        model = os.environ.get("OPENAI_MODEL", "")
        signin_enabled = os.environ.get("NMI_ENABLE_CHATGPT_SIGNIN") == "1"
        plan_model = os.environ.get('NMI_CHATGPT_MODEL','')
        allow_api = os.environ.get('NMI_ENABLE_PAID_API') == '1'
        app = create_app(access_token=token, enabled=enabled, model=model, signin_enabled=signin_enabled,
                         plan_model=plan_model,allow_api=allow_api, provider=provider,
                         claude_model=claude_model, allow_claude=allow_claude, max_calls=max_calls)
        logging.getLogger("werkzeug").disabled = True
        if provider == 'claude':
            allow_api, signin_enabled = False, False
        print("Local single-tester NMI. AI " + (f"ENABLED ({max_calls} attempt(s) per launch)" if enabled else "DISABLED"), flush=True)
        if provider == 'claude':
            print('Claude selected. Anthropic paid inference ' + ('ENABLED' if allow_claude else 'DISABLED') +
                  '. Model ' + ('configured' if valid_claude_model(claude_model) else 'NOT CONFIGURED') +
                  '. Both OpenAI providers inactive.', flush=True)
        print("ChatGPT sign-in " + ("ENABLED" if signin_enabled else "DISABLED") +
              ". Sign-in does not enable inference.", flush=True)
        print('Paid API billing ' + ('ENABLED by explicit owner setting' if allow_api else 'DISABLED') +
              '. ChatGPT model ' + ('configured' if plan_model else 'NOT CONFIGURED'), flush=True)
        print(f"Open privately: http://127.0.0.1:8766/#local-access={token}", flush=True)
        app.run(host="127.0.0.1", port=8766, debug=False, use_reloader=False, load_dotenv=False)


if __name__ == "__main__":
    main()
