"""
Récupération du token KFC via l'API users (association carte fidélité).

Paramètres alignés sur le storage : id, carte, prenom, nom, email, numero, ddb.
ddb est envoyé tel quel dans le champ dob ; jour, mois, annee sont déduits de ddb.

Usage:
    result = await recup_token(
        id="uuid",
        carte="123456789",
        prenom="Jean",
        nom="Dupont",
        email="jean@example.com",
        numero="0612345678",
        ddb="1990-01-15",
    )
    if result[0] == "success":
        account_id, token = result[1], result[2]
    else:
        error_code, error_message = result[1], result[2]
"""
import json
import re
import ssl
from typing import Optional, Tuple, Union

import aiohttp

TIMEOUT = 20
MAX_RETRIES = 3
BASE_URL = "https://13.248.197.133/api/users"


def _parse_ddb(ddb: str) -> Tuple[int, int, int]:
    """
    Extrait jour, mois, annee depuis ddb (format storage).
    Accepte YYYY-MM-DD ou DD/MM/YYYY. Retourne (jour, mois, annee).
    """
    if not ddb or not isinstance(ddb, str):
        return 1, 1, 2000
    s = ddb.strip()
    # YYYY-MM-DD
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return int(m.group(3)), int(m.group(2)), int(m.group(1))
    # DD/MM/YYYY
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return 1, 1, 2000


def _build_payload(
    idd: str,
    login: str,
    name1: str,
    name2: str,
    mail: str,
    num: str,
    ddn: str,
    jour: int,
    mois: int,
    annee: int,
    gender: Optional[str] = None,
    marketing_opt_in: bool = False,
    subscribe_channel: Optional[list] = None,
) -> str:
    """Construit le payload JSON pour la requête."""
    if subscribe_channel is None:
        subscribe_channel = [0, 0]
    payload = {
        "loyaltyId": login,
        "id": idd,
        "gender": gender,
        "firstName": name1,
        "lastName": name2,
        "phoneNumber": num,
        "email": mail,
        "marketingOptIn": marketing_opt_in,
        "birthYear": annee,
        "birthMonth": mois,
        "subscribeChannel": subscribe_channel,
        "birthDay": jour,
        "dob": ddn,
    }
    return json.dumps(payload)


async def recup_token(
    id: str,
    carte: str,
    prenom: str,
    nom: str,
    email: str,
    numero: str,
    ddb: str,
    gender: Optional[str] = None,
    marketing_opt_in: bool = False,
    subscribe_channel: Optional[list] = None,
    timeout: int = TIMEOUT,
    max_retries: int = MAX_RETRIES,
) -> Tuple[str, Union[Tuple[str, str], Tuple[str, str, str]]]:
    """
    Effectue la requête POST pour associer une carte fidélité au compte KFC
    et récupère le token de la réponse.

    Args (alignés storage):
        id: ID du compte utilisateur (UUID)
        carte: Numéro de carte fidélité
        prenom: Prénom (ex. saisi par l'utilisateur pour la commande)
        nom: Nom de famille
        email: Email
        numero: Numéro de téléphone
        ddb: Date de naissance (format storage, envoyée telle quelle dans dob)
        gender, marketing_opt_in, subscribe_channel: optionnels
        timeout, max_retries: config

    Returns:
        ("success", id, token) si succès
        ("error", error_code, error_message) si erreur
    """
    if not id or not carte:
        return ("error", "invalid_params", "id et carte sont requis")

    jour, mois, annee = _parse_ddb(ddb)
    ddn = ddb if ddb else ""

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    client_timeout = aiohttp.ClientTimeout(total=timeout)
    payload = _build_payload(
        idd=id,
        login=carte,
        name1=prenom,
        name2=nom,
        mail=email,
        num=numero,
        ddn=ddn,
        jour=jour,
        mois=mois,
        annee=annee,
        gender=gender,
        marketing_opt_in=marketing_opt_in,
        subscribe_channel=subscribe_channel,
    )

    headers = {
        "Sec-CH-UA-Platform": '"Windows"',
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Sec-CH-UA": '"Not_A Brand";v="99", "Chromium";v="142"',
        "Sec-CH-UA-Mobile": "?0",
        "Culturecode": "fr",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.kfc.fr",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.kfc.fr/my-account/edit",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=1, i",
    }

    last_error_code = ""
    last_error_msg = ""

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.post(
                    f"{BASE_URL}/{id}",
                    data=payload,
                    headers=headers,
                    ssl=ssl_ctx,
                ) as response:
                    raw_text = await response.text()

                    if response.status >= 500:
                        last_error_code = "server_error"
                        last_error_msg = f"Serveur indisponible (HTTP {response.status})"
                        continue

                    if response.status >= 400:
                        last_error_code = "http_error"
                        last_error_msg = f"HTTP {response.status} - {raw_text[:200] if raw_text else '(vide)'}"
                        return ("error", last_error_code, last_error_msg)

                    if not raw_text or not raw_text.strip():
                        last_error_code = "empty_response"
                        last_error_msg = "Réponse vide du serveur"
                        continue

                    try:
                        data = json.loads(raw_text)
                    except json.JSONDecodeError as e:
                        last_error_code = "invalid_json"
                        last_error_msg = f"Contenu invalide (JSON) : {str(e)[:100]}"
                        continue

                    token = data.get("token")
                    if not token or not isinstance(token, str) or not token.strip():
                        errors_obj = data.get("errors") or {}
                        errors_list = errors_obj.get("errors") if isinstance(errors_obj, dict) else []
                        err_details = ", ".join(str(e) for e in errors_list[:3]) if errors_list else "Token absent"
                        last_error_code = "no_token"
                        last_error_msg = f"Token non récupéré : {err_details}"
                        return ("error", last_error_code, last_error_msg)

                    return ("success", id, token.strip())

        except aiohttp.ServerTimeoutError:
            last_error_code = "timeout"
            last_error_msg = f"Timeout après {timeout}s (tentative {attempt + 1}/{max_retries})"
        except aiohttp.ClientError as e:
            last_error_code = "connection_error"
            last_error_msg = f"Erreur de connexion : {str(e)[:150]}"
        except aiohttp.ClientConnectorError as e:
            last_error_code = "server_unreachable"
            last_error_msg = f"Serveur injoignable : {str(e)[:150]}"
        except Exception as e:
            last_error_code = "unexpected_error"
            last_error_msg = f"Erreur inattendue : {str(e)[:150]}"

    return ("error", last_error_code or "max_retries", last_error_msg or "Échec après toutes les tentatives")
