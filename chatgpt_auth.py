"""Official local SIWC public client. Tokens live only in this process, never on disk."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import threading
import time
from urllib.parse import urlencode, urlsplit
from uuid import UUID, uuid4

import httpx2 as httpx
import jwt

ISSUER = "https://auth.openai.com"
AUTHORIZE = ISSUER + "/api/accounts/authorize"
TOKEN = ISSUER + "/api/accounts/oauth/token"
JWKS = ISSUER + "/.well-known/jwks.json"
DISCOVERY = ISSUER + "/.well-known/openid-configuration"
RESOURCE = "https://api.openai.com/v1"
SCOPES = "openid profile email offline_access resource.invoke chatgpt.tokens.use.direct"
DIRECT = "chatgpt.tokens.use.direct"
CLIENT_ID = re.compile(r"oaiapp_[A-Za-z0-9_-]{1,240}")


class AuthError(Exception):
    """Only fixed public error codes cross the Flask boundary."""
    def __init__(self, code="oauth"):
        self.code = code
        super().__init__(code)


class OfficialTransport:
    def request(self, method, url, *, data=None, bearer=None):
        # Neither redirects nor environment proxy/base-URL overrides may receive tokens.
        allowed = {DISCOVERY, JWKS, TOKEN, RESOURCE + "/models"}
        parsed = urlsplit(url)
        revoke = (parsed.scheme == "https" and parsed.netloc == "auth.openai.com"
                  and parsed.path.startswith("/") and not parsed.query and not parsed.fragment)
        if url not in allowed and not (method == "POST" and revoke):
            raise AuthError()
        try:
            with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as client:
                response = client.request(method, url, data=data,
                    headers={"Authorization": "Bearer " + bearer} if bearer else {})
                if len(response.content) > 1_000_000:
                    raise AuthError()
                if response.status_code == 200:
                    return response.json() if response.content else {}
                payload = response.json() if response.content else {}
                error = payload.get("error") if isinstance(payload, dict) else None
                code = error.get("code") if isinstance(error, dict) else error
                if code in {"invalid_grant", "invalid_refresh_token", "token_expired",
                            "refresh_token_expired", "refresh_token_invalidated", "refresh_token_reused"}:
                    raise AuthError("signin")
                raise AuthError("oauth")
        except AuthError:
            raise
        except Exception:
            raise AuthError("oauth") from None


class ChatGPTAuth:
    """One local account registration. No construction-time I/O or authentication."""
    def __init__(self, registration_path, redirect_uri, *, transport=None, clock=time.time):
        uri = urlsplit(redirect_uri)
        if uri.scheme != "http" or uri.hostname != "127.0.0.1" or uri.path != "/auth/callback" or not uri.port or uri.query or uri.fragment:
            raise ValueError("A fixed loopback callback is required")
        self.path = Path(registration_path)
        self.redirect_uri = redirect_uri
        self.transport = transport or OfficialTransport()
        self.clock = clock
        self.lock = threading.RLock()
        self.registration = None
        self.pending = None
        self.credentials = None
        self.models = []
        self.selected_model = ""
        self.last_error = None

    def _load(self):
        if self.registration is not None:
            return
        if not self.path.exists():
            self.registration = {"host_id": "urn:uuid:" + str(uuid4()), "client_id": None, "subject": None}
            self._save()
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if set(data) != {"host_id", "client_id", "subject"}:
                raise ValueError()
            host = data["host_id"]
            if not isinstance(host, str) or not host.startswith("urn:uuid:") or str(UUID(host[9:])) != host[9:]:
                raise ValueError()
            if data["client_id"] is not None and not CLIENT_ID.fullmatch(data["client_id"]):
                raise ValueError()
            if data["subject"] is not None and (not isinstance(data["subject"], str) or not data["subject"] or len(data["subject"]) > 512):
                raise ValueError()
            self.registration = data
        except Exception:
            raise AuthError("storage") from None

    def _save(self):
        # Registration metadata only: never place token fields here.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(self.path.name + ".tmp-" + secrets.token_hex(8))
        try:
            with temporary.open("x", encoding="utf-8") as handle:
                json.dump(self.registration, handle)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        except OSError:
            raise AuthError("storage") from None

    def public_state(self):
        with self.lock:
            connected = self.credentials is not None
            return {"connected": connected, "sharing": connected and {DIRECT, "resource.invoke"} <= self.credentials["scopes"],
                    "models": list(self.models), "model": self.selected_model,
                    "error": self.last_error}

    def start(self):
        with self.lock:
            self._load()
            if self.pending and self.pending["expires"] > self.clock():
                raise AuthError("busy")
            verifier = secrets.token_urlsafe(48)
            state, nonce = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            cid = self.registration["client_id"]
            self.pending = dict(state=state, nonce=nonce, verifier=verifier,
                                client_id=cid, expires=self.clock() + 300)
            params = dict(client_id=cid or "dynamic_agent_client", response_type="code",
                          redirect_uri=self.redirect_uri, resource=RESOURCE, scope=SCOPES,
                          ext_agent_host_id=self.registration["host_id"], state=state, nonce=nonce,
                          code_challenge_method="S256",
                          code_challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode())
            if not cid:
                params["agent_name_hint"] = "NMI"
            elif self.credentials and not {DIRECT, "resource.invoke"} <= self.credentials["scopes"]:
                params["prompt"] = "consent"
            # Deliberately omit login/ID-token hints: no credentials enter a URL.
            self.last_error = None
            return AUTHORIZE + "?" + urlencode(params)

    def _verify(self, encoded, client_id, nonce=None):
        try:
            if not isinstance(encoded, str) or len(encoded) > 32000:
                raise ValueError()
            header = jwt.get_unverified_header(encoded)
            # Reject algorithm confusion and token-controlled key URLs.
            if header.get("alg") not in {"RS256", "ES256"} or not isinstance(header.get("kid"), str):
                raise ValueError()
            keys = self.transport.request("GET", JWKS)["keys"]
            matching = [key for key in keys if key.get("kid") == header["kid"]
                        and key.get("use", "sig") == "sig" and key.get("alg", header["alg"]) == header["alg"]]
            if len(matching) != 1:
                raise ValueError()
            key = jwt.PyJWK.from_dict(matching[0], algorithm=header["alg"]).key
            claims = jwt.decode(encoded, key, algorithms=[header["alg"]], audience=client_id,
                                issuer=ISSUER, options={"require": ["exp", "iss", "aud", "sub", "iat"]})
            if not isinstance(claims["sub"], str) or not claims["sub"] or len(claims["sub"]) > 512:
                raise ValueError()
            if (isinstance(claims["aud"], list) and len(claims["aud"]) > 1) or "azp" in claims:
                if claims.get("azp") != client_id:
                    raise ValueError()
            if nonce is not None and (not isinstance(claims.get("nonce"), str) or not secrets.compare_digest(claims["nonce"], nonce)):
                raise ValueError()
            return claims["sub"]
        except Exception:
            raise AuthError("oauth") from None

    def _tokens(self, data, previous=None):
        try:
            scope = data.get("scope")
            if scope is None and previous:
                scopes = previous["scopes"]
            elif isinstance(scope, str):
                scopes = set(scope.split())
            else:
                raise ValueError()
            # A verified identity-only grant may carry no resource credentials.
            # Retain the connection, but never enable inference or fabricate a token.
            if not {DIRECT, "resource.invoke"} <= scopes:
                refresh = data.get("refresh_token")
                if refresh is not None and (not isinstance(refresh, str) or not refresh or len(refresh) > 64000):
                    raise ValueError()
                return dict(access_token=None, refresh_token=refresh, scopes=scopes, expires=self.clock())
            if data.get("token_type", "").lower() != "bearer":
                raise ValueError()
            expires = data["expires_in"]
            if type(expires) not in (int, float) or not 0 < expires <= 86400:
                raise ValueError()
            access = data["access_token"]
            refresh = data.get("refresh_token")
            if not isinstance(access, str) or not access or len(access) > 64000:
                raise ValueError()
            if refresh is not None and (not isinstance(refresh, str) or not refresh or len(refresh) > 64000):
                raise ValueError()
            return dict(access_token=access, refresh_token=refresh, scopes=scopes,
                        expires=self.clock() + expires)
        except Exception:
            raise AuthError() from None

    def finish(self, query):
        with self.lock:
            pending = self.pending
            supplied = query.get("state", "")
            if not pending or not isinstance(supplied, str) or not secrets.compare_digest(supplied, pending["state"]):
                raise AuthError("oauth")
            self.pending = None  # One-use, including failed/declined/expired attempts.
            if pending["expires"] <= self.clock():
                raise AuthError("oauth")
            if query.get("error"):
                self.last_error = "consent"
                raise AuthError("consent")
            cid = query.get("client_id", pending["client_id"])
            code = query.get("code")
            if not isinstance(cid, str) or not CLIENT_ID.fullmatch(cid) or (pending["client_id"] and cid != pending["client_id"]):
                raise AuthError()
            if not isinstance(code, str) or not code or len(code) > 8192:
                raise AuthError()
            # Retain the issued registration even if its first code expires.
            self.registration["client_id"] = cid
            self._save()
            data = self.transport.request("POST", TOKEN, data=dict(grant_type="authorization_code",
                client_id=cid, code=code, code_verifier=pending["verifier"],
                redirect_uri=self.redirect_uri, resource=RESOURCE))
            subject = self._verify(data.get("id_token"), cid, pending["nonce"])
            if self.registration["subject"] not in (None, subject):
                raise AuthError("account")
            tokens = self._tokens(data)
            self.registration["subject"] = subject
            self._save()
            self.credentials = tokens
            self.models, self.selected_model = [], ""
            self.last_error = None if {DIRECT, "resource.invoke"} <= tokens["scopes"] else "consent"

    def access_token(self):
        with self.lock:
            if not self.credentials:
                raise AuthError("signin")
            old = self.credentials
            if DIRECT not in old["scopes"] or "resource.invoke" not in old["scopes"]:
                raise AuthError("consent")
            if old["expires"] <= self.clock() + 30:
                if not old["refresh_token"]:
                    raise AuthError("signin")
                try:
                    data = self.transport.request("POST", TOKEN, data=dict(grant_type="refresh_token",
                        client_id=self.registration["client_id"], refresh_token=old["refresh_token"], resource=RESOURCE))
                    if data.get("id_token"):
                        if self._verify(data["id_token"], self.registration["client_id"]) != self.registration["subject"]:
                            raise AuthError("account")
                    replacement = self._tokens(data, old)
                    if {DIRECT, "resource.invoke"} <= replacement["scopes"] and not replacement["refresh_token"]:
                        raise AuthError()
                    self.credentials = replacement
                    if not {DIRECT, "resource.invoke"} <= replacement["scopes"]:
                        self.models, self.selected_model = [], ""
                        self.last_error = "consent"
                except AuthError as error:
                    if error.code in {"signin", "account"}:
                        self.credentials = None
                        self.models, self.selected_model = [], ""
                    raise
            if not {DIRECT, "resource.invoke"} <= self.credentials["scopes"]:
                raise AuthError("consent")
            return self.credentials["access_token"]

    def load_models(self):
        with self.lock:
            payload = self.transport.request("GET", RESOURCE + "/models", bearer=self.access_token())
            try:
                values = payload["models"]
                if not isinstance(values, list) or len(values) > 1000:
                    raise ValueError()
                models = []
                for item in values:
                    if item.get("visibility") != "list":
                        continue
                    slug, label = item["slug"], item["display_name"]
                    if not isinstance(slug, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", slug) or not isinstance(label, str) or not 0 < len(label) <= 200:
                        raise ValueError()
                    if slug not in {m["slug"] for m in models}:
                        models.append(dict(slug=slug, display_name=label))
            except Exception:
                raise AuthError("model") from None
            self.models = models
            if self.selected_model not in {item["slug"] for item in models}:
                self.selected_model = ""
            return models

    def select_model(self, slug):
        with self.lock:
            if not isinstance(slug, str) or slug not in {item["slug"] for item in self.models}:
                raise AuthError("model")
            self.selected_model = slug

    def sign_out(self):
        with self.lock:
            confirmed = True
            try:
                if self.credentials and self.credentials["refresh_token"]:
                    config = self.transport.request("GET", DISCOVERY)
                    url = config["revocation_endpoint"]
                    parts = urlsplit(url)
                    if config.get("issuer") != ISSUER or parts.scheme != "https" or parts.netloc != "auth.openai.com" or parts.query or parts.fragment:
                        raise AuthError()
                    self.transport.request("POST", url, data=dict(token=self.credentials["refresh_token"],
                        token_type_hint="refresh_token", client_id=self.registration["client_id"]))
            except Exception:
                confirmed = False
            finally:
                self.credentials, self.pending = None, None
                self.models, self.selected_model = [], ""
                self.last_error = None if confirmed else "revocation"
            return confirmed
