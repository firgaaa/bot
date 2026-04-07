from .kfc_api import baskets
from typing import Optional



def NewBasket(storeId: str, userToken: str = None) -> Optional[str]:
    """
    Create a new basket for the specified store and return its ID.

    This function acts as a wrapper around the corresponding API endpoint.

    Args:
        storeId (str): Target store's id. Refer to the doc

    Returns:
        basketUUID (str | None): The basket's UUID, or None if an error occurred.
    """
    
    basket = baskets.CreateBasket(storeId, userToken)
    if basket == None:
        return None

    return basket['id']



def GetBasketById(basketUUID: str, userToken: str = None) -> Optional[dict]:
    """
    Retrieve informations about the given basket via the API.

    This function acts as a wrapper around the corresponding API endpoint.

    Args:
        basketUUID (str): Target basket's UUID. Refer to the doc

    Returns:
        apiResponse (Optional[dict]): The response of the api, or None if an error occurred.
    """

    basket = baskets.GetBasketInfo(basketUUID, userToken)
    if basket == None:
        return None

    return basket



def AddLoyaltyItemToBasket(
    basketUUID: str,
    loyaltyId: str,
    loyaltyPrice: int,
    quantity: int,
    modgrps: list[dict] = [],
    userToken: str = None,
) -> Optional[dict]:
    """
    Add the specified item to the given basket via the API.

    This function acts as a wrapper around the corresponding API endpoint.

    Args:
        basketUUID (str): Target basket's UUID. Refer to the doc
        loyaltyId (str): Item's loyalty id. Refer to the doc
        loyaltyPrice (int): Item's loyalty price. Refer to the doc
        quantity (int): Item's quantity. Refer to the doc
        modgrps (list): Item's selected modgrps. Refer to the doc

    Returns:
        apiResponse (dict): The response of the api (should be a dict containing added item's information), or None if an error occurred.
    """

    r = baskets.AddLoyaltyItem(
        basketUUID,
        loyaltyId,
        loyaltyPrice,
        quantity,
        modgrps,
        userToken=userToken,
    )
    
    if r == None:
        return None

    return r

def RemoveLoyaltyItemFromBasket(basketUUID: str, itemUUID: str, userToken: str = None) -> Optional[dict]: #You 
    """
    Remove the specified item from the given basket via the API.

    This function acts as a wrapper around the corresponding API endpoint.

    Args:
        basketUUID (str): Target basket's UUID. Refer to the doc
        itemUUID (str): Target item's UUID in the basket. Refer to the doc

    Returns:
        apiResponse (list[tuple[str, str]]): The response of the api (should be a empty dict in this case), or None if an error occurred.
    """

    r = baskets.RemoveLoyaltyItem(basketUUID, itemUUID, userToken=userToken)
    
    if r == None:
        return None

    return r

    