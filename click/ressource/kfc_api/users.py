from .helper import HTTPGet, HTTPPost, HTTPPut
from . import COOKIES

def _auth_header(userToken: str = None) -> str:
    token = str(userToken or "").strip()
    return f"Bearer {token}" if token else ""

def GetUserInfo(userUUID: str, userToken: str=None):

    url = f"https://www.kfc.fr/api/users/{userUUID}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr,fr-FR;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.kfc.fr/paiement",
        "Culturecode": "fr",
        "Authorization": _auth_header(userToken),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "Te": "trailers",
    }

    cookies = COOKIES

    r, c = HTTPGet(url, headers=headers, cookies=cookies)

    if r == None:
        print(f"[-] {c}")
        return None

    return r.json()

    #8d375c42649cbe6ed595db91aa01cbd54e840b64b0b0aa3b8dbc4019de8c5b95

def GetUserLoyaltyInfo(userUUID: str, userToken: str=None):
    url = f"https://www.kfc.fr/api/users/{userUUID}/loyaltyinfo"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "fr,fr-FR;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Authorization": _auth_header(userToken),
        "cache-control": "no-cache",
        "culturecode": "fr",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.kfc.fr/loyalty",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Microsoft Edge";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
        ),
    }

    cookies = COOKIES

    r, c = HTTPGet(url, headers=headers, cookies=cookies)

    if r == None:
        print(f"[-] {c}")
        return None

    return r.json()

def GetUserLoyaltyPointsExpireDateInfo(userUUID: str, userToken: str=None):
    url = f"https://www.kfc.fr/api/users/{userUUID}/loyaltypointexpiredate"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "fr,fr-FR;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Authorization": _auth_header(userToken),
        "cache-control": "no-cache",
        "culturecode": "fr",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.kfc.fr/loyalty",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Microsoft Edge";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
        ),
    }

    cookies = COOKIES

    r, c = HTTPGet(url, headers=headers, cookies=cookies)

    if r == None:
        print(f"[-] {c}")
        return None

    return r.json()


def SendUILog(message: str, userToken: str=None):
    url = "https://www.kfc.fr/api/uiloginfo"

    headers = {
        "Host": "www.kfc.fr",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr,fr-FR;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.kfc.fr/paiement",
        "Culturecode": "fr",
        "Content-Type": "application/json",
        "Authorization": _auth_header(userToken),
        "Origin": "https://www.kfc.fr",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "Te": "trailers",
    }

    cookies = COOKIES

    payload = {
        "error": "Info",
        "message": message
    }

    r, c = HTTPPost(url, headers=headers, cookies=cookies, json=payload)
    if r == None:
        return None

    return c

def RegisterBasket(userId: str, basketId: str, firstName, lastName, phoneNumber, email, recaptchaToken, userToken: str=None):

    url = f"https://www.kfc.fr/api/users/{userId}/baskets/{basketId}/registeredsubmit"

    headers = {
        "Host": "www.kfc.fr",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr,fr-FR;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.kfc.fr/prise-de-commande",
        "Culturecode": "fr",
        "Content-Type": "application/json",
        "Authorization": _auth_header(userToken),
        "Origin": "https://www.kfc.fr",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Te": "trailers",
    }

    cookies = COOKIES

    payload = {
        "customer": {
            "id": userId,
            "firstName": firstName,
            "lastName": lastName,
            "phoneNumber": phoneNumber,
            "email": email,
            "password": ""
        },
        "tender": "cash",
        "savedCardId": None,
        "deliveryAddress": None,
        "fulfillment": {
            "asap": True,
            "scheduled": {
                "date": "",
                "key": "",
                "time": ""
            }
        },
        "acceptTermConditions": True,
        "saveCard": False,
        "existingCard": False,
        "posType": "Aloha",
        "recaptchaToken": recaptchaToken
    }

    r, c = HTTPPost(url, headers=headers, cookies=cookies, json=payload)

    if r == None:
        print(f"[-] {c}")
        return None

    return r.json()