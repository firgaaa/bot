"""
Async : POST KFC /api/login → GET Xitroo /v1/mails (poll paramétrable) → POST twostep.
Pas de cookies (DummyCookieJar). Résultat par ligne : mail, code, twostep, error, time (durée en secondes).

Comptes : fichier JSONL produit par export_kfc_credentials.py (défaut : kfc_credentials.jsonl à côté de ce script).

Suivi : tableau live (rich) + récapitulatif en fin d'exécution. Les résultats détaillés ne sont plus affichés (restent en mémoire).

Fichier deja_ajouter : e-mails déjà traités avec succès (PUT /update OK). Ignorés au lancement (cas « déjà récupéré ») ; les nouvelles réussites y sont ajoutées à la fin.

Dépendances : pip install aiohttp pycryptodome rich
"""
import argparse
import asyncio
import base64
import json
import random
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

try:
    from rich.console import Group
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad

# Fichier par défaut : même répertoire que ce script (aligné sur export_kfc_credentials.py)
DEFAULT_CREDENTIALS_JSONL = Path(__file__).resolve().parent / "kfc_credentials.jsonl"
# E-mails déjà traités avec succès (token enregistré via PUT /update) — un e-mail normalisé par ligne
DEFAULT_DEJA_AJOUTER = Path(__file__).resolve().parent / "deja_ajouter"

BEARER_TOKEN = ""  # optionnel Xitroo

API_BASE_URL = "https://api.xitroo.com"
KFC_API_BASE = "https://13.248.197.133"
KFC_VERIFY_SSL = False
LOCAL_UPDATE_URL = "http://localhost:8080/update"
LOCAL_API_USER = "clemser"
LOCAL_API_PASS = "root"

@dataclass
class BearerRunConfig:
    """Limites pour gros volumes : défauts plus agressifs (vitesse). Réduire via CLI si Xitroo/KFC limite."""

    # Comptes dont le pipeline (login → Xitroo → twostep → update) est actif en parallèle
    account_concurrency: int = 28
    # Requêtes HTTP simultanées vers l’API KFC (login + twostep)
    kfc_http_concurrency: int = 40
    # Polls GET Xitroo simultanés (souvent le goulot d’étranglement)
    xitroo_http_concurrency: int = 18
    # PUT vers l’API locale /update
    update_http_concurrency: int = 48
    request_timeout_s: int = 45
    # Temps max pour recevoir le mail après login (secondes)
    xitroo_poll_max_sec: float = 90.0
    xitroo_poll_sleep_sec: float = 0.25
    # minTimestamp = now − fenêtre : doit couvrir délais d’envoi KFC en masse
    xitroo_window_sec: int = 300


DEFAULT_RUN_CONFIG = BearerRunConfig()

# Chiffrement login (identique à test_postdata.py)
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
  MIGeMA0GCSqGSIb3DQEBAQUAA4GMADCBiAKBgHO4AqKut5xbco9jgfz+bqkx9v0M
O9t5DGzZEltqqZE5tNzHbve2D+KPWTeD+G9q2PilkPPHRz2+r5MgwlD4dGP6zum3
hNj27CCIgUeaIJGhX/JlmBO3bgFGCcuemuKc+ygFJYvf0RzCo5svfn/6cKSHeovl
orMqQbQU3GrHLVA9AgMBAAE=
  -----END PUBLIC KEY-----"""
IV = "@qwertyuiop12344"

EXPECTED_LOGIN_RESPONSE: Dict[str, Any] = {
    "token": None,
    "user": None,
    "resetPasswordLink": None,
    "refreshToken": None,
    "errors": None,
    "isAuthSuccessful": False,
    "is2StepVerificationRequired": True,
    "provider": "Email",
}

_CODE_RE = re.compile(r"^\d{6}$")


def load_accounts_from_jsonl(path: Path) -> List[Tuple[str, str, str]]:
    """Lit kfc_credentials.jsonl : une ligne JSON avec customer_id, email, password."""
    if not path.is_file():
        raise FileNotFoundError(str(path))
    out: List[Tuple[str, str, str]] = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{line_no} JSON invalide : {e}") from e
            c = obj.get("customer_id")
            m = obj.get("email")
            p = obj.get("password")
            cs = str(c).strip() if c is not None else ""
            ms = str(m).strip() if m is not None else ""
            ps = "" if p is None else str(p)
            if cs and ms:
                out.append((cs, ms, ps))
    return out


def normalize_email(email: str) -> str:
    return email.strip().lower()


def load_deja_emails(path: Path) -> set[str]:
    """Charge les e-mails déjà enregistrés (lignes non vides, sans commentaires #)."""
    if not path.is_file():
        return set()
    out: set[str] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            out.add(normalize_email(s))
    return out


def append_new_emails_to_deja_file(path: Path, emails: List[str]) -> int:
    """
    Ajoute en fin de fichier les e-mails absents (comparaison en minuscules).
    Retourne le nombre de lignes réellement ajoutées.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_deja_emails(path)
    to_write: List[str] = []
    for raw in emails:
        n = normalize_email(raw)
        if not n or n in existing:
            continue
        existing.add(n)
        to_write.append(n)
    if not to_write:
        return 0
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for e in to_write:
            f.write(f"{e}\n")
    return len(to_write)


def make_deja_recuperer_result(customer_id: str, mail: str) -> Dict[str, Any]:
    """Résultat synthétique pour un compte déjà listé dans deja_ajouter."""
    return {
        "customer_id": customer_id,
        "mail": mail.strip(),
        "code": None,
        "twostep": None,
        "update_status": None,
        "update_status_mapped": None,
        "update_result": None,
        "error": None,
        "time": 0.0,
        "outcome_override": "deja_recuperer",
    }


OUTCOME_ORDER = (
    "success",
    "deja_recuperer",
    "invalid_input",
    "login_failed",
    "xitroo_failed",
    "twostep_failed",
    "update_failed",
    "other",
)

OUTCOME_LABELS: Dict[str, str] = {
    "success": "Réussite complète",
    "deja_recuperer": "Déjà récupéré (fichier deja_ajouter)",
    "invalid_input": "Entrée invalide (mail / mot de passe)",
    "login_failed": "Échec login KFC",
    "xitroo_failed": "Échec Xitroo / code e-mail",
    "twostep_failed": "Échec twostep",
    "update_failed": "Échec PUT /update (API locale)",
    "other": "Autre / non classé",
}


def classify_outcome(d: Dict[str, Any]) -> str:
    """Catégorise un résultat renvoyé par process_account."""
    if d.get("outcome_override") == "deja_recuperer":
        return "deja_recuperer"
    err_raw = d.get("error")
    err = (err_raw or "").strip().lower()
    cid = d.get("customer_id")

    if not err:
        return "success" if cid else "other"

    if "mail invalide" in err or "mot de passe vide" in err:
        return "invalid_input"
    if err.startswith("login:") or "chiffrement" in err:
        return "login_failed"
    if "xitroo:" in err or "aucun email" in err:
        return "xitroo_failed"
    if "twostep:" in err:
        return "twostep_failed"
    if "update:" in err:
        return "update_failed"
    return "other"


def outcome_counter(results: List[Dict[str, Any]]) -> Counter:
    return Counter(classify_outcome(r) for r in results)


def _build_live_panel(counts: Counter, done: int, total: int, elapsed: float) -> Panel:
    table = Table(show_header=True, header_style="bold")
    table.add_column("Cas", style="dim")
    table.add_column("Nombre", justify="right")
    for key in OUTCOME_ORDER:
        table.add_row(OUTCOME_LABELS[key], str(counts.get(key, 0)))
    footer = Text.from_markup(
        f"[bold]{done}[/bold] / {total} comptes · [cyan]{elapsed:.1f}[/cyan] s écoulés"
    )
    return Panel(Group(table, Text(""), footer), title="KFC bearer — progression", expand=False)


def print_final_recap(results: List[Dict[str, Any]], elapsed_sec: float) -> None:
    total = len(results)
    counts = outcome_counter(results)
    ok = counts.get("success", 0)

    lines = [
        "",
        "— Récapitulatif —",
        f"  Comptes traités   : {total}",
        f"  Durée totale      : {elapsed_sec:.3f} s",
        f"  Réussites         : {ok}" + (f" ({100.0 * ok / total:.1f}%)" if total else ""),
        "",
        "  Détail par cas :",
    ]
    for key in OUTCOME_ORDER:
        n = counts.get(key, 0)
        if total:
            pct = 100.0 * n / total
            lines.append(f"    {OUTCOME_LABELS[key]} : {n} ({pct:.1f}%)")
        else:
            lines.append(f"    {OUTCOME_LABELS[key]} : {n}")
    lines.append("")
    print("\n".join(lines))


def now_ts_10() -> int:
    return int(time.time())


def generate_key() -> str:
    chars = "@abcdefghijklmnopqrstuvwxyz123456789"
    return "".join(random.choice(chars) for _ in range(16))


def encrypt_aes(text: str, key: str) -> str:
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, IV.encode("utf-8"))
    padded = pad(text.encode("utf-8"), AES.block_size)
    return base64.b64encode(cipher.encrypt(padded)).decode("utf-8")


def encrypt_rsa(text: str) -> str:
    rsa_key = RSA.import_key(PUBLIC_KEY)
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypted = cipher.encrypt(text.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def encrypt_login_payload(email: str, password: str) -> str:
    aes_key = generate_key()
    data = {
        "email": encrypt_aes(email, aes_key),
        "password": encrypt_aes(password, aes_key),
    }
    return json.dumps(
        {
            "data": encrypt_aes(json.dumps(data, separators=(",", ":")), aes_key),
            "key": encrypt_rsa(aes_key),
        },
        separators=(",", ":"),
    )


# Profils cohérents : User-Agent + Client Hints (même « famille » navigateur)
_BROWSER_PROFILES: Tuple[Dict[str, str], ...] = (
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Google Chrome";v="130", "Chromium";v="130", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Google Chrome";v="129", "Chromium";v="129", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Google Chrome";v="128", "Chromium";v="128", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Google Chrome";v="126", "Chromium";v="126", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Sec-Ch-Ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Sec-Ch-Ua": '"Microsoft Edge";v="130", "Chromium";v="130", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Google Chrome";v="124", "Chromium";v="124", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Google Chrome";v="121", "Chromium";v="121", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Mobile": "?0",
    },
)

_ACCEPT_LANGS: Tuple[str, ...] = (
    "fr-FR,fr;q=0.9",
    "fr-FR,fr;q=0.9,en-US;q=0.5",
    "fr,fr-FR;q=0.9",
    "fr-FR,fr;q=0.9,en;q=0.6",
)


def random_browser_profile() -> Dict[str, str]:
    """Profil UA + Client Hints + Accept-Language (fixe pour tout le traitement d’un compte)."""
    p = dict(random.choice(_BROWSER_PROFILES))
    p["Accept-Language"] = random.choice(_ACCEPT_LANGS)
    return p


def _merge_ua_profile(ua_profile: Dict[str, str]) -> Dict[str, str]:
    m = dict(ua_profile)
    if "Accept-Language" not in m:
        m["Accept-Language"] = random.choice(_ACCEPT_LANGS)
    return m


def build_xitroo_headers(ua_profile: Dict[str, str]) -> Dict[str, str]:
    ua = _merge_ua_profile(ua_profile)
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        **ua,
        "Origin": "https://xitroo.fr",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://xitroo.fr/",
        "Priority": "u=1, i",
    }
    if BEARER_TOKEN.strip():
        headers["Authorization"] = f"Bearer {BEARER_TOKEN.strip()}"
    return headers


def build_kfc_login_headers(ua_profile: Dict[str, str]) -> Dict[str, str]:
    ua = _merge_ua_profile(ua_profile)
    return {
        **ua,
        "Culturecode": "fr",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.kfc.fr",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.kfc.fr/mon-compte/connexion?returnUrl=%2F",
        "Priority": "u=1, i",
    }


def build_kfc_twostep_headers(ua_profile: Dict[str, str]) -> Dict[str, str]:
    ua = _merge_ua_profile(ua_profile)
    return {
        **ua,
        "Culturecode": "fr",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.kfc.fr",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Priority": "u=1, i",
    }


def validate_login_response(data: Any) -> Optional[str]:
    if not isinstance(data, dict):
        return "login: réponse JSON objet attendu"
    for key, expected in EXPECTED_LOGIN_RESPONSE.items():
        if key not in data:
            return f"login: clé manquante {key!r}"
        if data[key] != expected:
            return (
                f"login: {key!r} attendu {expected!r}, reçu {data[key]!r}"
            )
    return None


def decode_body_html_strict_base64(body_b64: str) -> str:
    raw = body_b64.strip()
    padding = (-len(raw)) % 4
    if padding:
        raw += "=" * padding
    try:
        decoded = base64.b64decode(raw, validate=True)
    except Exception as e:
        raise RuntimeError(f"bodyHtmlStrict base64 invalide: {e}")
    return decoded.decode("utf-8", errors="replace")


def extract_kfc_code(html: str) -> str:
    m = re.search(r"<b>\s*(\d{6})\s*</b>", html, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{6})\b", html)
    if m:
        return m.group(1)
    raise RuntimeError("code 6 chiffres introuvable dans le HTML")


def first_mail_id(data: Dict[str, Any]) -> Optional[str]:
    mails = data.get("mails")
    if not isinstance(mails, list) or not mails:
        return None
    first = mails[0]
    if not isinstance(first, dict):
        return None
    _id = first.get("_id")
    if isinstance(_id, str) and _id.strip():
        return _id.strip()
    return None


def extract_code_from_mails_json(data: Dict[str, Any]) -> str:
    mails = data.get("mails")
    if not isinstance(mails, list) or not mails:
        raise RuntimeError("mails: tableau vide ou absent")
    first = mails[0]
    if not isinstance(first, dict):
        raise RuntimeError("mails[0]: objet attendu")
    body = first.get("bodyHtmlStrict")
    if not isinstance(body, str) or not body.strip():
        raise RuntimeError("bodyHtmlStrict absent ou vide")
    html = decode_body_html_strict_base64(body.strip())
    code = extract_kfc_code(html)
    if not _CODE_RE.match(code):
        raise RuntimeError(f"code invalide (attendu 6 chiffres): {code!r}")
    return code


def parse_twostep_result(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text
    if isinstance(data, dict) and "token" in data:
        t = data.get("token")
        if t is not None and t != "":
            return str(t)
    return text


def empty_result(mail: str, error: str, elapsed_sec: float) -> Dict[str, Any]:
    return {
        "mail": mail,
        "code": None,
        "twostep": None,
        "error": error,
        "time": round(elapsed_sec, 3),
    }


def ok_result(
    customer_id: str,
    mail: str,
    code: Optional[str],
    twostep: Optional[str],
    error: Optional[str],
    elapsed_sec: float,
    update_status: Optional[int] = None,
    update_status_mapped: Optional[int] = None,
    update_result: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "customer_id": customer_id,
        "mail": mail,
        "code": code,
        "twostep": twostep,
        "update_status": update_status,
        "update_status_mapped": update_status_mapped,
        "update_result": update_result,
        "error": error,
        "time": round(elapsed_sec, 3),
    }


async def post_login(
    session: aiohttp.ClientSession,
    mail: str,
    password: str,
    sem: asyncio.Semaphore,
    ua_profile: Dict[str, str],
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Retourne (ok, json_dict_ou_None, message_erreur_ou_vide)."""
    url = f"{KFC_API_BASE}/api/login"
    try:
        body_str = encrypt_login_payload(mail, password)
    except Exception as e:
        return False, None, f"login: chiffrement payload: {e}"

    headers = build_kfc_login_headers(ua_profile)
    async with sem:
        try:
            async with session.post(
                url,
                data=body_str.encode("utf-8"),
                headers=headers,
                ssl=KFC_VERIFY_SSL,
            ) as resp:
                raw = await resp.text()
        except asyncio.TimeoutError:
            return False, None, "login: timeout"
        except aiohttp.ClientError as e:
            return False, None, f"login: réseau {e}"

    if resp.status != 200:
        return False, None, f"login: HTTP {resp.status} {raw[:800]}"

    try:
        data = json.loads(raw) if raw.strip() else None
    except json.JSONDecodeError:
        return False, None, f"login: JSON illisible {raw[:800]}"

    err = validate_login_response(data)
    if err:
        return False, None, f"{err} | corps={raw[:800]}"

    return True, data if isinstance(data, dict) else None, ""


async def get_xitroo_code(
    session: aiohttp.ClientSession,
    mail: str,
    sem: asyncio.Semaphore,
    ua_profile: Dict[str, str],
    *,
    poll_max_sec: float,
    window_sec: int,
    poll_sleep_sec: float,
) -> Tuple[bool, str, str]:
    """Boucle jusqu'à _id + code extrait. minTimestamp = now − window_sec (secondes)."""
    deadline = time.monotonic() + poll_max_sec
    saw_id = False
    last_extract_err = ""

    url = f"{API_BASE_URL}/v1/mails"
    x_headers = build_xitroo_headers(ua_profile)

    while time.monotonic() < deadline:
        now = now_ts_10()
        min_ts = max(0, now - window_sec)
        params = {
            "locale": "fr",
            "mailAddress": mail,
            "mailsPerPage": 1,
            "minTimestamp": min_ts,
            "maxTimestamp": now,
        }

        async with sem:
            try:
                async with session.get(url, params=params, headers=x_headers) as resp:
                    raw = await resp.text()
            except asyncio.TimeoutError:
                return False, "", "xitroo: timeout"
            except aiohttp.ClientError as e:
                return False, "", f"xitroo: réseau {e}"

        if resp.status != 200:
            return False, "", f"xitroo: HTTP {resp.status} {raw[:800]}"

        try:
            data = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            return False, "", f"xitroo: JSON illisible {raw[:800]}"

        if not isinstance(data, dict):
            return False, "", "xitroo: réponse JSON objet attendu"

        _id = first_mail_id(data)
        if not _id:
            await asyncio.sleep(poll_sleep_sec)
            continue

        saw_id = True
        try:
            code = extract_code_from_mails_json(data)
            return True, code, ""
        except Exception as e:
            last_extract_err = f"{e} | corps={raw[:800]}"
            await asyncio.sleep(poll_sleep_sec)

    if saw_id:
        return False, "", f"xitroo: {last_extract_err or 'extraction code échouée'}"

    return False, "", "aucun email recu"


async def post_twostep(
    session: aiohttp.ClientSession,
    mail: str,
    code: str,
    sem: asyncio.Semaphore,
    ua_profile: Dict[str, str],
) -> Tuple[bool, str, str]:
    """Retourne (ok, twostep_value_ou_vide, erreur)."""
    url = f"{KFC_API_BASE}/api/twostepverification"
    payload = {"email": mail, "provider": "Email", "token": code}
    headers = build_kfc_twostep_headers(ua_profile)
    async with sem:
        try:
            async with session.post(
                url,
                json=payload,
                headers=headers,
                ssl=KFC_VERIFY_SSL,
            ) as resp:
                raw = await resp.text()
        except asyncio.TimeoutError:
            return False, "", "twostep: timeout"
        except aiohttp.ClientError as e:
            return False, "", f"twostep: réseau {e}"

    if resp.status != 200:
        return False, "", f"twostep: HTTP {resp.status} {raw[:800]}"

    if not raw.strip():
        return False, "", "twostep: corps vide"

    return True, parse_twostep_result(raw), ""


def map_update_status(status_code: int) -> str:
    normalized = map_update_status_code(status_code)
    if normalized == 204:
        return "OK"
    if normalized == 404:
        return "INTROUVABLE"
    return "ERREUR"


def map_update_status_code(status_code: int) -> int:
    if status_code == 204:
        return 204
    if status_code == 404:
        return 404
    return 500


async def put_update_token(
    session: aiohttp.ClientSession,
    customer_id: str,
    bearer_token: str,
    sem: asyncio.Semaphore,
    ua_profile: Dict[str, str],
) -> Tuple[bool, int, str]:
    """
    Retourne (ok, status_http, message).
    ok=True uniquement si HTTP 204.
    """
    payload = {
        "customer_id": customer_id,
        "bearer_token": bearer_token,
    }
    auth = aiohttp.BasicAuth(LOCAL_API_USER, LOCAL_API_PASS)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": ua_profile.get(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        ),
    }
    async with sem:
        try:
            async with session.put(
                LOCAL_UPDATE_URL,
                auth=auth,
                json=payload,
                headers=headers,
            ) as resp:
                raw = await resp.text()
        except asyncio.TimeoutError:
            return False, 500, "update: timeout"
        except aiohttp.ClientError as e:
            return False, 500, f"update: réseau {e}"

    status = int(resp.status)
    if status == 204:
        return True, status, ""
    if status == 404:
        return False, status, "update: customer_id introuvable"
    return False, status, f"update: HTTP {status} {raw[:800]}"


async def process_account(
    session: aiohttp.ClientSession,
    customer_id: str,
    mail: str,
    password: str,
    sem_kfc: asyncio.Semaphore,
    sem_xitroo: asyncio.Semaphore,
    sem_update: asyncio.Semaphore,
    cfg: BearerRunConfig,
) -> Dict[str, Any]:
    t0 = time.perf_counter()

    def elapsed() -> float:
        return time.perf_counter() - t0

    mail = mail.strip()
    if not mail or "@" not in mail:
        return empty_result(mail or "", "mail invalide", elapsed())
    if not password:
        return empty_result(mail, "mot de passe vide", elapsed())

    ua = random_browser_profile()

    ok, _, err = await post_login(session, mail, password, sem_kfc, ua)
    if not ok:
        return empty_result(mail, err or "login: échec", elapsed())

    ok2, code, err2 = await get_xitroo_code(
        session,
        mail,
        sem_xitroo,
        ua,
        poll_max_sec=cfg.xitroo_poll_max_sec,
        window_sec=cfg.xitroo_window_sec,
        poll_sleep_sec=cfg.xitroo_poll_sleep_sec,
    )
    if not ok2:
        return empty_result(mail, err2 or "xitroo: échec", elapsed())

    ok3, twostep_val, err3 = await post_twostep(session, mail, code, sem_kfc, ua)
    if not ok3:
        return ok_result(
            customer_id,
            mail,
            code,
            None,
            err3 or "twostep: échec",
            elapsed(),
        )

    ok4, update_status, err4 = await put_update_token(
        session, customer_id, twostep_val, sem_update, ua
    )
    update_status_mapped = map_update_status_code(update_status)
    update_result = map_update_status(update_status)
    if not ok4:
        return ok_result(
            customer_id,
            mail,
            code,
            twostep_val,
            err4 or "update: échec",
            elapsed(),
            update_status=update_status,
            update_status_mapped=update_status_mapped,
            update_result=update_result,
        )

    return ok_result(
        customer_id,
        mail,
        code,
        twostep_val,
        None,
        elapsed(),
        update_status=update_status,
        update_status_mapped=update_status_mapped,
        update_result=update_result,
    )


async def run_all(
    accounts: List[Tuple[str, str, str]],
    deja_path: Path,
    cfg: BearerRunConfig = DEFAULT_RUN_CONFIG,
) -> List[Dict[str, Any]]:
    deja_set = load_deja_emails(deja_path)
    n = len(accounts)
    results_by_index: List[Optional[Dict[str, Any]]] = [None] * n
    pending: List[Tuple[int, str, str, str]] = []

    for i, (c, m, p) in enumerate(accounts):
        if normalize_email(m) in deja_set:
            results_by_index[i] = make_deja_recuperer_result(c, m)
        else:
            pending.append((i, c, m, p))

    counts: Counter = Counter()
    for slot in results_by_index:
        if slot is not None:
            counts[classify_outcome(slot)] += 1

    total = n
    done_list = [sum(1 for x in results_by_index if x is not None)]
    lock = asyncio.Lock()
    t0 = time.perf_counter()
    live_ref: Dict[str, Any] = {"live": None}

    def refresh_ui() -> None:
        elapsed = time.perf_counter() - t0
        d = done_list[0]
        if _RICH_AVAILABLE and live_ref["live"] is not None:
            live_ref["live"].update(_build_live_panel(counts, d, total, elapsed))
        elif not _RICH_AVAILABLE:
            print(
                f"\r[{d}/{total}] ok={counts.get('success', 0)} "
                f"déjà={counts.get('deja_recuperer', 0)}",
                file=sys.stderr,
                end="",
                flush=True,
            )

    if not pending:
        return [results_by_index[i] for i in range(n)]  # type: ignore[list-item]

    timeout = aiohttp.ClientTimeout(total=cfg.request_timeout_s)
    per_host = max(
        cfg.kfc_http_concurrency,
        cfg.xitroo_http_concurrency,
        cfg.update_http_concurrency,
        cfg.account_concurrency * 3,
        32,
    )
    connector = aiohttp.TCPConnector(limit=0, limit_per_host=per_host)
    cookie_jar = aiohttp.DummyCookieJar()

    account_sem = asyncio.Semaphore(cfg.account_concurrency)
    sem_kfc = asyncio.Semaphore(cfg.kfc_http_concurrency)
    sem_xitroo = asyncio.Semaphore(cfg.xitroo_http_concurrency)
    sem_update = asyncio.Semaphore(cfg.update_http_concurrency)

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        cookie_jar=cookie_jar,
    ) as session:

        async def wrapped(idx: int, c: str, m: str, p: str) -> None:
            async with account_sem:
                r = await process_account(
                    session,
                    c,
                    m,
                    p,
                    sem_kfc,
                    sem_xitroo,
                    sem_update,
                    cfg,
                )
            async with lock:
                results_by_index[idx] = r
                counts[classify_outcome(r)] += 1
                done_list[0] += 1
                refresh_ui()

        if _RICH_AVAILABLE:
            initial_elapsed = time.perf_counter() - t0
            initial = _build_live_panel(counts, done_list[0], total, initial_elapsed)
            with Live(initial, refresh_per_second=10, transient=True) as live:
                live_ref["live"] = live
                await asyncio.gather(*[wrapped(i, c, m, p) for i, c, m, p in pending])
            live_ref["live"] = None
        else:
            print(
                "(Installez le package 'rich' pour le tableau de suivi.)\n",
                file=sys.stderr,
            )
            await asyncio.gather(*[wrapped(i, c, m, p) for i, c, m, p in pending])
            print(file=sys.stderr)

    return [results_by_index[i] for i in range(n)]  # type: ignore[list-item]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Login KFC + codes Xitroo + twostep (comptes depuis JSONL)"
    )
    parser.add_argument(
        "-f",
        "--credentials-file",
        type=Path,
        default=DEFAULT_CREDENTIALS_JSONL,
        help=f"Fichier JSONL (défaut : {DEFAULT_CREDENTIALS_JSONL.name})",
    )
    parser.add_argument(
        "--deja-file",
        type=Path,
        default=DEFAULT_DEJA_AJOUTER,
        help=f"Fichier des e-mails déjà récupérés (défaut : {DEFAULT_DEJA_AJOUTER.name})",
    )
    parser.add_argument(
        "--account-concurrency",
        type=int,
        default=DEFAULT_RUN_CONFIG.account_concurrency,
        metavar="N",
        help="Comptes traités en parallèle (pipeline complet). Défaut : %(default)s",
    )
    parser.add_argument(
        "--kfc-concurrency",
        type=int,
        default=DEFAULT_RUN_CONFIG.kfc_http_concurrency,
        metavar="N",
        help="Requêtes KFC (login + twostep) simultanées. Défaut : %(default)s",
    )
    parser.add_argument(
        "--xitroo-concurrency",
        type=int,
        default=DEFAULT_RUN_CONFIG.xitroo_http_concurrency,
        metavar="N",
        help="Polls GET api.xitroo.com simultanés. Défaut : %(default)s",
    )
    parser.add_argument(
        "--update-concurrency",
        type=int,
        default=DEFAULT_RUN_CONFIG.update_http_concurrency,
        metavar="N",
        help="PUT /update simultanés. Défaut : %(default)s",
    )
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=DEFAULT_RUN_CONFIG.request_timeout_s,
        metavar="SEC",
        help="Timeout HTTP par requête (secondes). Défaut : %(default)s",
    )
    parser.add_argument(
        "--xitroo-poll-sec",
        type=float,
        default=DEFAULT_RUN_CONFIG.xitroo_poll_max_sec,
        metavar="SEC",
        help="Durée max d’attente du mail après login. Défaut : %(default)s",
    )
    parser.add_argument(
        "--xitroo-window-sec",
        type=int,
        default=DEFAULT_RUN_CONFIG.xitroo_window_sec,
        metavar="SEC",
        help="Fenêtre minTimestamp (now − N) pour l’API Xitroo. Défaut : %(default)s",
    )
    args = parser.parse_args()
    path = args.credentials_file.resolve()
    deja_path = args.deja_file.resolve()

    for name, val in (
        ("account-concurrency", args.account_concurrency),
        ("kfc-concurrency", args.kfc_concurrency),
        ("xitroo-concurrency", args.xitroo_concurrency),
        ("update-concurrency", args.update_concurrency),
        ("request-timeout", args.request_timeout),
        ("xitroo-window-sec", args.xitroo_window_sec),
    ):
        if val < 1:
            print(f"Argument --{name} doit être >= 1 (reçu : {val})", file=sys.stderr)
            raise SystemExit(2)
    if args.xitroo_poll_sec <= 0:
        print("--xitroo-poll-sec doit être > 0", file=sys.stderr)
        raise SystemExit(2)

    cfg = BearerRunConfig(
        account_concurrency=args.account_concurrency,
        kfc_http_concurrency=args.kfc_concurrency,
        xitroo_http_concurrency=args.xitroo_concurrency,
        update_http_concurrency=args.update_concurrency,
        request_timeout_s=args.request_timeout,
        xitroo_poll_max_sec=args.xitroo_poll_sec,
        xitroo_window_sec=args.xitroo_window_sec,
    )

    try:
        accounts = load_accounts_from_jsonl(path)
    except FileNotFoundError:
        print(
            f"Fichier introuvable : {path}\n"
            f"Générez-le avec : python export_kfc_credentials.py",
            file=sys.stderr,
        )
        raise SystemExit(1)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(1)

    if not accounts:
        print("Aucun compte à traiter (fichier vide ou aucune ligne valide).", file=sys.stderr)
        return

    print(
        f"Concurrence : comptes={cfg.account_concurrency}, KFC={cfg.kfc_http_concurrency}, "
        f"Xitroo={cfg.xitroo_http_concurrency}, update={cfg.update_http_concurrency} | "
        f"poll Xitroo={cfg.xitroo_poll_max_sec}s, fenêtre={cfg.xitroo_window_sec}s\n",
        file=sys.stderr,
    )

    t_run = time.perf_counter()
    results = asyncio.run(run_all(accounts, deja_path, cfg))
    elapsed = time.perf_counter() - t_run
    # Résultats détaillés conservés dans `results` (pas d'affichage JSON).
    print_final_recap(results, elapsed)

    success_mails = [
        str(r["mail"])
        for r in results
        if classify_outcome(r) == "success" and r.get("mail")
    ]
    added = append_new_emails_to_deja_file(deja_path, success_mails)
    if added:
        print(f"  Fichier deja_ajouter : +{added} e-mail(s) → {deja_path}")
        print()


if __name__ == "__main__":
    main()
