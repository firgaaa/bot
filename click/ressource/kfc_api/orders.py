from .helper import HTTPGet, HTTPPost, HTTPPut
from . import COOKIES

def _auth_header(userToken: str = None) -> str:
    token = str(userToken or "").strip()
    return f"Bearer {token}" if token else ""

def SendCheckin(orderUUID: str, userToken=None):
    url = f"https://www.kfc.fr/api/order/{orderUUID}/checkin"

    headers = {
        "Host": "www.kfc.fr",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr,fr-FR;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": f"https://www.kfc.fr/confirmation-de-commande/{orderUUID}",
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

    data = {
        "intent": "instore",
        "recaptchaToken": "",
        "posType": "Aloha"
    }

    r, c = HTTPPost(url, headers=headers, cookies=cookies, json=data)

    if r == None:
        print(f"[-] {c}")
        return None

    return r.json()

def GetOrder(orderId: str, userToken: str = None):
    url = f"https://api.kfc.fr/orders/{orderId}"

    headers = {
        "Host": "api.kfc.fr",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr,fr-FR;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.kfc.fr",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Authorization": _auth_header(userToken),
        "Te": "trailers",
    }

    r, c = HTTPGet(url, headers=headers)

    if r == None:
        print(f"[-] {c}")
        return None

    return r.json()