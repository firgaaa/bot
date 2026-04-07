import base64
import re
import time
from typing import Any, Dict, Optional

import requests

# Script 100% indépendant: modifie juste ces constantes.
MAIL = "lw90ehlgpr@xitroo.fr"
BEARER_TOKEN = ""  # optionnel (sinon laisse vide)

API_BASE_URL = "https://api.xitroo.com"
TIMEOUT_S = 20


def now_ts_10() -> int:
    # Timestamp UNIX en secondes (10 chiffres)
    return int(time.time())


def build_headers() -> Dict[str, str]:
    headers = {
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
        ),
        "Sec-Ch-Ua-Mobile": "?0",
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


def get_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    resp = requests.get(url, params=params, headers=build_headers(), timeout=TIMEOUT_S)
    data = resp.json() if resp.content else {}
    if resp.status_code >= 400:
        msg = data.get("message") if isinstance(data, dict) else None
        raise RuntimeError(msg or f"HTTP {resp.status_code}")
    if not isinstance(data, dict):
        raise RuntimeError("Réponse invalide (JSON attendu)")
    return data


def fetch_latest_id(mail: str) -> str:
    data = get_json(
        f"{API_BASE_URL}/v1/mails",
        {
            "locale": "fr",
            "mailAddress": mail,
            "mailsPerPage": 1,
            "minTimestamp": 0,
            "maxTimestamp": now_ts_10(),
        },
    )
    mails = data.get("mails", [])
    if isinstance(mails, list) and mails and isinstance(mails[0], dict):
        body = mails[0].get("bodyHtmlStrict")
        if isinstance(body, str) and body.strip():
            return body.strip()
    raise RuntimeError(str(data.get("message") or "bodyHtmlStrict introuvable dans mails[0]"))


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
    # Cas le plus fréquent: le code est dans un <b>058884</b>
    m = re.search(r"<b>\s*(\d{6})\s*</b>", html, flags=re.IGNORECASE)
    if m:
        return m.group(1)

    # Fallback: premier bloc de 6 chiffres (évite d'être trop strict)
    m = re.search(r"\b(\d{6})\b", html)
    if m:
        return m.group(1)

    raise RuntimeError("code 6 chiffres introuvable dans le HTML")


def main() -> int:
    mail = MAIL.strip()
    if not mail or "@" not in mail:
        print("erreur: MAIL invalide (définis MAIL en haut du fichier)")
        return 1

    try:
        body_b64 = fetch_latest_id(mail)
        html = decode_body_html_strict_base64(body_b64)
        code = extract_kfc_code(html)
    except Exception as e:
        print(f"erreur: {e}")
        return 1

    print(code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

