from .kfc_api import stores
from .account import GetAccountLoyaltyInfo, GetUserLoyaltyPointsExpireDateInfo

import sys

def LoyaltyMatch(loyaltyInfo, menuInfo):
    """
    Matching the loyalty's info from the account to the loyalty category of the store to determine the real loyalty menu.

    Args:
        loyaltyInfo (str): Account's loyalty info. Refer to the doc
        menuInfo (str): Store's loyalty category. Refer to the doc

    Returns:
        loyaltyMenu (tuple[dict, int]): tuple containing info about the store's menu and the matched item number. Refer to the doc
    """
    res = {}

    n = 0
    for i in range(len(loyaltyInfo)):
        
        Group = loyaltyInfo[i]
        GroupItems = Group["items"]

        res[Group['name']] = []
        for j in range(len(GroupItems)):
            alohaItemId = str(GroupItems[j]['itemId']['alohaItemId'])
            amrestItemId = str(GroupItems[j]['itemId']['amrestItemId'])

            StoreLoyaltyProducts = menuInfo["products"]
            StoreLoyaltyProducts_len = len(StoreLoyaltyProducts)

            k = 0
            while k < StoreLoyaltyProducts_len:
                pos_raw = StoreLoyaltyProducts[k]['items'][0].get('posItemId', '')
                if isinstance(pos_raw, dict):
                    store_pos = str(pos_raw.get('alohaItemId', '') or pos_raw.get('amrestItemId', ''))
                else:
                    store_pos = str(pos_raw)
                if store_pos == alohaItemId or store_pos == amrestItemId:
                    break
                k += 1

            if k != StoreLoyaltyProducts_len: #Successful match
                #print(f"{Group['name']} | {StoreLoyaltyProducts[k]['items'][0]['name']} : {GroupItems[j]['points']}")
                n+=1
                data = {
                    "name" : StoreLoyaltyProducts[k]['items'][0]['name'],
                    "id" : StoreLoyaltyProducts[k]['items'][0]['id'],
                    "cost" : GroupItems[j]['points']
                }

                if "modgrps" in StoreLoyaltyProducts[k]['items'][0].keys():
                    data["modgrps"] = StoreLoyaltyProducts[k]['items'][0]['modgrps']

                res[Group['name']].append(data)

    return res, n



def GetLoyaltyFromStore(storeId: str) -> dict:
    """
    Retrieve the loyalty category of the menu in the selected store. This function is not precise, don't use it alone, use GetLoyaltyMenu instead.

    Args:
        storeId (str): store's Id. Refer to the doc

    Returns:
        loyaltyCategory (dict): dict containing the loyalty category of the store's menu, None if an error occured.
    """
    storeMenu = stores.GetStoreMenu(storeId)
    if storeMenu == None:
        return None

    categories = storeMenu['categories'][0]['categories']
    categories_len = len(categories)

    i = 0
    while i < categories_len and categories[i]['name'] != "LOYALTY":
        i += 1
    
    if i == categories_len:
        return None

    return categories[i]



# Nombre d'items fidélité attendus pour un restaurant supporté Click & Collect
LOYALTY_MATCH_COUNT_SUPPORTED = 35


def GetStoreLoyaltyMatchCount(accountId: str, storeId: str, accountToken: str=None):
    """
    Retourne le nombre d'items fidélité matchés pour ce restaurant.
    Retourne None en cas d'erreur.
    Si == LOYALTY_MATCH_COUNT_SUPPORTED (35), le restaurant est supporté pour le Click & Collect.
    """
    loyaltyInfo = GetAccountLoyaltyInfo(accountId, accountToken)
    if loyaltyInfo is None:
        return None
    loyaltyInfo = loyaltyInfo["rewards"]
    storeLoyalty = GetLoyaltyFromStore(storeId)
    if storeLoyalty is None:
        return None
    _, matched_count = LoyaltyMatch(loyaltyInfo, storeLoyalty)
    return matched_count


def GetLoyaltyMenu(accountId: str, storeId: str, accountToken: str=None) -> tuple[dict, int]:
    """
    Retrieve the loyalty menu of the selected store.

    Args:
        accountId (str): Account Id. Refer to the doc
        accountToken (str): Account Token. Refer to the doc
        storeId (str): store's Id. Refer to the doc

    Returns:
        menuInfo (dict): tuple containing info about the store's menu, None if an error occured. Refer to the doc
    """

    loyaltyInfo = GetAccountLoyaltyInfo(accountId, accountToken)
    if loyaltyInfo == None:
        #print(f"[-] Pas pu avoir infos de compte")
        return None
    
    loyaltyInfo = loyaltyInfo["rewards"]
    
    storeLoyalty = GetLoyaltyFromStore(storeId)
    if storeLoyalty == None:
        #print(f"[-] Pas pu avoir infos du resto")
        return None

    loyaltyInfo = LoyaltyMatch(loyaltyInfo, storeLoyalty)

    loyaltyMenu = loyaltyInfo[0]
    matchedItem = loyaltyInfo[1]

    #print(matchedItem)

    print(f"[?] Is place available for pickup order : {matchedItem == 35}")
    if matchedItem != 35:
        print(f"This restaurant is probably not supported")
        a = input("Do you want to continue ? [Y/N] ")
        if a == "N":
            sys.exit(1)

    
    return loyaltyMenu



def ChooseLoyalty(loyaltyMenu: dict) -> dict:
    """
    Function used to select the product from loyaltyMenu, you may need to edit this or make your own selection system if its you're not using CLI.

    Args:
        loyaltyMenu (dict): product's modgrps group. Refer to the doc

    Returns:
        itemInfo (dict): dict containing info about the selected product, None if an error occured. Refer to the doc
    """
    categories = list(loyaltyMenu.keys())

    # ---- Choose category ----
    print("\n=== Categories ===")
    for i, category in enumerate(categories):
        print(f"{i + 1}. {category}")

    cat_index = int(input("Select category: ")) - 1
    selected_category = categories[cat_index]

    items = loyaltyMenu[selected_category]

    # ---- Choose item ----
    print(f"\n=== {selected_category} ===")
    for i, item in enumerate(items):
        print(f"{i + 1}. {item['name']} ({item['cost']} pts)")

    item_index = int(input("Select item: ")) - 1
    selected_item = items[item_index]

    # ---- Return only required fields ----

    data = {
        "name": selected_item["name"],
        "id": selected_item["id"],
        "cost": selected_item["cost"],
    }

    if "modgrps" in selected_item.keys():
        data["modgrps"] =  selected_item['modgrps']

    return data