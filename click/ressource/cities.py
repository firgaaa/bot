import unicodedata

from .kfc_api import stores, helper
from .geohash import Geohash


def RemoveAccents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(
        c for c in normalized
        if unicodedata.category(c) != "Mn"
    )


def GetMatchingPlace2(allStores, place):
    matched = []
    lowerPlace = RemoveAccents(place.lower())
    for i in range(len(allStores)):
        store = allStores[i]
        storeName = RemoveAccents(store["name"].lower())
        storeCity = RemoveAccents(store["city"].lower())
        storeAddress = RemoveAccents(store["address"].lower())
        if lowerPlace in storeName or lowerPlace in storeCity or lowerPlace in storeAddress:
            matched.append((store["name"], store["city"], store["id"]))

    if len(matched) <= 0:
        return None
    
    return matched



def ChooseKFC() -> tuple[str, str]:
    """
    CLI implemention to choose a KFC. You may need to edit this or make your own selection system if its you're not using CLI.

    Args:
        

    Returns:
        kfcInfo (tuple[str, str]): The (name, id) tuple of the chosen KFC, or None if an error occurred. See documentation for details.
    """
    allStores = stores.GetAllStores()
    if allStores == None:
        print(f"[+] Failed to use allStores endpoint")
        return None
    
    user_city = input("Ville > ")
    matched = GetMatchingPlace2(allStores, user_city)
    if matched == None:
        print("[-] Pas de KFC trouvé")
        return None
    
    for i in range(len(matched)):
        print(f"{i+1}) {matched[i][0]} | {matched[i][1]}")

    choice_i = int(input("\nChoice > ")) - 1
    KFC = matched[choice_i]

    return KFC