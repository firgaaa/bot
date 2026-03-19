from .kfc_api import baskets, orders, users, braze
from .account import GetUserInfo, SubmitBasket
from .basket import GetBasketById
from .recaptcha import GetRecaptchaToken

import json

def CheckoutBasket(basketUUID: str, userToken:str=None):
    """
    Checkout the specified basket. Similar to clicking "Order" in the basket page. More information in the doc

    Args:
        basketUUID (str): Basket UUID. Refer to the doc
        userToken (str): User's Token. Refer to the doc

    Returns:
        Bool: True if no error happened, False else.
    """
    basketJson = GetBasketById(basketUUID)
    if basketJson == None:
        print(f"[-] GetBasket Error")
        return None

    itemNumber = len(basketJson["items"])
    orderTotalPrice = basketJson["total"]

    code = users.SendUILog(f"UI - Checkout Page viewed for basket ID {basketUUID} , items in basket- {itemNumber} order total - {orderTotalPrice}", userToken)
    #print(f"[{code}] UILog - Checkout Page viewed for basket ID {basketUUID} , items in basket- {itemNumber} order total - {orderTotalPrice}")

    code = braze.SendBrazeEventSS()
    #print(f"[{code}] Braze SS")

    return True

def SubmitOrder(basketUUID, basketItems, userUUID, userToken=None, user_info=None):
    """
    Submit the specified basket. Similar to clicking "Complete" in the ordering page. More information in the doc

    Args:
        basketUUID (str): Basket UUID. Refer to the doc
        basketItems (str): A dict list containing the baskets. Refer to the doc
        userUUID (str): User's UUID. Refer to the doc
        userToken (str): User's Token. Refer to the doc
        user_info (dict, optional): If provided, use instead of calling GetUserInfo (évite un double appel).

    Returns:
        Tuple: (orderUUID, orderNumber) if no error happened, (None, None) else.
    """
    if user_info is not None:
        User = user_info
    else:
        User = GetUserInfo(userUUID, userToken)
    if User is None:
        print(f"[-] GetUserInfo Error")
        return None, None

    userId = User.get('id')
    firstName = User.get('firstName') or User.get('first_name') or ''
    lastName = User.get('lastName') or User.get('last_name') or ''
    phoneNumber = User.get('phoneNumber') or User.get('phone_number') or ''
    email = User.get('email') or ''
    #print(f"[+] GetUser -> {basketUUID}, {userId}, {firstName}, {lastName}, {phoneNumber}, {email}")
    


    code = users.SendUILog(f"UI - Order submission started for the basket id - {basketUUID}", userToken)
    #print(f"[{code}] UI - Order submission started for the basket id - {basketUUID}")


    
    code = baskets.AssociateToAccount(basketUUID, userId, firstName, lastName, phoneNumber, email)
    if code == None:
        print(f"[-] AssociateToAccount Error")
        return None, None
    #print(f"[{code}] PutBasketInfo")



    recaptchaToken = GetRecaptchaToken()
    #print(f"[+] GetRecaptchaToken Success")


    
    OrderInfo = SubmitBasket(userUUID, basketUUID, firstName, lastName, phoneNumber, email, recaptchaToken, userToken)
    if OrderInfo == None:
        print(f"[-] SubmitBasket Error")
        return None, None
    
    orderNumber = OrderInfo['orderNumber'] #Used for IRL (940003828)
    orderUUID = OrderInfo['orderIdTracker'] #Used for web tracking (a8bcdc12-6b54-40bb-9867-cbf18d976b02)
    #print(f"[+] SendRegisteredSubmit Success -> {orderNumber} {orderUUID}")

    code = users.SendUILog(f"UI - Submit Order- Order submitted successfully for basket id -{basketUUID} , OrderTrackerNumber - {orderNumber}", userToken) #IRL
    #print(f"[{code}] UI - Submit Order- Order submitted successfully for basket id -{basketUUID} , OrderTrackerNumber - {orderNumber}") #IRL

    #MyBasket.GetCurrent()

    code = users.SendUILog(f"UI - Order Confirmation paged viewed for Order hash - {orderUUID}", userToken) #Web
    #print(f"[{code}] UI - Order Confirmation paged viewed for Order hash - {orderUUID}") #Web

    basket = GetBasketById(basketUUID)
    if basket == None:
        print(f"[-] GetBasketById Error")
        return None, None
    
    StoreName = basket['storeName']

    code = braze.SendBrazeEventCommandComplete(StoreName, basketItems)
    #print(f"[{code}] Braze CommandComplete")

    return orderUUID, orderNumber



def CheckinOrder(orderUUID, userToken=None): #When you're ready/near restaurant
    """
    Checking the specified order. Similar to clicking "I'm here" in the last page. More information in the doc

    Args:
        orderUUID (str): Order UUID. Refer to the doc
        accountToken (str): Account Token. Refer to the doc

    Returns:
        Bool: True if no error happened, False else.
    """
    Order = orders.GetOrder(orderUUID)
    if Order == None:
        print(f"[-] GetOrder Error")
        return None
    #print(f"[+] GetOrder Success")
    


    code = users.SendUILog(f"UI - Checkin process started for Order Id {orderUUID}", userToken)
    #print(f"[{code}] UI - Checkin process started for Order Id {orderUUID}")



    canCheckin = 'true' if Order['checkin']['possible'] else 'false'
    code = users.SendUILog(f"UI - Validating if checkin possible for Order Id {orderUUID} , status - {canCheckin}", userToken)
    #print(f"[{code}] UI - Validating if checkin possible for Order Id {orderUUID} , status - {canCheckin}")



    #print(json.dumps(Order))



    code = orders.SendCheckin(orderUUID, userToken)
    if code == None:
        print(f"[-] SendCheckin Error")
        return None
    #print(f"[{code}] SendCheckin Sucess (Order should start)")



    code = users.SendUILog(f"UI - Checkin successful for Order Id - {orderUUID}", userToken)
    #print(f"[{code}] UI - Checkin successful for Order Id - {orderUUID}")



    code = braze.SendBrazeCheckin()
    #print(f"[{code}] Braze Checkin")

    #Order = GetOrder(OrderId)
    #print(json.dumps(Order))

    return True
