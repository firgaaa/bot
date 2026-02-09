"""
Suppression : appelle l'API KFC pour supprimer un compte utilisateur (profil).

Fonction autonome : une seule entrée, pas de session ni callback externes.

Usage:
    result = await delete_account(profile)
    if result[0] == "success":
        # Compte supprimé
    elif result[0] == "echec":
        # API a renvoyé false
    else:
        error_code, error_message = result[1], result[2]
"""
import asyncio
import aiohttp
import os
import time
import ssl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG_PATH = os.path.join(SCRIPT_DIR, "suppression_error_log.txt")

TIMEOUT = 20
MAX_RETRIES = 3


def _log(error_type: str, message: str, idd: str) -> None:
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(ERROR_LOG_PATH, "a", encoding="utf-8", errors="ignore") as f:
            f.write(f"[{ts}] [{error_type}] id={idd!r} - {message}\n")
    except Exception:
        pass


async def delete_account(profile):
    """
    Appelle POST /api/users/{idd}/delete pour supprimer le compte.

    Args:
        profile: dict avec au moins "id" (idd utilisé dans l'URL).

    Returns:
        ("success",) si l'API renvoie true
        ("echec",) si l'API renvoie false
        ("error", error_code, error_message) pour erreurs réseau/HTTP/parsing.
    """
    if profile is None or profile == "erreur" or not isinstance(profile, dict) or not profile.get("id"):
        msg = "Profil invalide ou manquant (dict avec id)."
        _log("profile_invalid", msg, str(profile)[:50])
        return "error", "profile_invalid", msg

    idd = profile.get("id")

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "Content-Length": "0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Sec-Ch-Ua": '"Not(A:Brand";v="8", "Chromium";v="144"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Culturecode": "fr",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.kfc.fr",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.kfc.fr/my-account/delete",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=1, i",
    }

    for attempt in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"https://13.248.197.133/api/users/{idd}/delete",
                    headers=headers,
                    ssl=ssl_ctx,
                ) as response:
                    if response.status >= 400:
                        try:
                            body = (await response.text())[:200]
                        except Exception:
                            body = ""
                        msg = f"HTTP {response.status} - {body}"
                        _log("http_error", msg, str(idd))
                        return "error", "http_error", msg

                    try:
                        raw = await response.text()
                        # Réponse attendue : un booléen (true/false)
                        if raw.strip().lower() == "true":
                            return "success",
                        if raw.strip().lower() == "false":
                            _log("api_false", "API a renvoyé false", str(idd))
                            return "echec",
                        # Autre contenu
                        msg = f"Réponse inattendue (pas un booléen): {raw[:200]!r}"
                        _log("parse_error", msg, str(idd))
                        return "error", "parse_error", msg
                    except Exception as e:
                        msg = f"Erreur lecture/réponse: {e!r}"
                        _log("parse_error", msg, str(idd))
                        return "error", "parse_error", msg

        except asyncio.TimeoutError:
            msg = f"Timeout (tentative {attempt + 1}/{MAX_RETRIES})"
            _log("timeout", msg, str(idd))
            if attempt == MAX_RETRIES - 1:
                return "error", "timeout", msg
        except aiohttp.ClientError as e:
            msg = f"Erreur réseau: {e!r}"
            _log("network_error", msg, str(idd))
            if attempt == MAX_RETRIES - 1:
                return "error", "network_error", msg
        except Exception as e:
            msg = f"Erreur inattendue: {e!r}"
            _log("unexpected", msg, str(idd))
            return "error", "unexpected", msg

    return "error", "timeout", "Timeout après toutes les tentatives."


if __name__ == "__main__":
    import sys
    # Test: python suppression_log.py <id>
    idd = sys.argv[1] if len(sys.argv) > 1 else "12345"
    profile = {"id": idd}
    out = asyncio.run(delete_account(profile))
    print(out)
