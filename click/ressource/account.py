from .kfc_api import users
from typing import Optional


def GetAccountLoyaltyInfo(userUUID: str, userToken: str=None) -> Optional[dict]:
    """
    Retrieve loyalty information of the account. 
    
    The API endpoint used is a bit heavy and inaccurate, you may use GetUserLoyaltyPointsExpireDateInfo in some case (doesn't contain menu !)

    This function acts as a wrapper around the corresponding API endpoint.

    Args:
        userUUID (str): Target users's UUID. Refer to the doc
        userToken (str): Target users's Token. Refer to the doc

    Returns:
        loyaltyInfo (dict | None): The account's loyalty informations, or None if an error occurred. Refer to the doc
    """
    loyaltyInfo = users.GetUserLoyaltyInfo(userUUID, userToken)
    if loyaltyInfo == None:
        return None

    return loyaltyInfo

def GetUserLoyaltyPointsExpireDateInfo(userUUID: str, userToken: str=None) -> Optional[dict]:
    """
    Retrieve loyalty information of the account.

    This function acts as a wrapper around the corresponding API endpoint.

    Args:
        userUUID (str): Target users's UUID. Refer to the doc
        userToken (str): Target users's Token. Refer to the doc

    Returns:
        loyaltyInfo (dict | None): The account's loyalty informations, or None if an error occurred. Refer to the doc
    """
    loyaltyInfo = users.GetUserLoyaltyPointsExpireDateInfo(userUUID, userToken)
    if loyaltyInfo == None:
        return None

    return loyaltyInfo

def GetUserInfo(userUUID: str, userToken: str=None) -> Optional[dict]:
    """
    Retrieve informations about the user.

    This function acts as a wrapper around the corresponding API endpoint.

    Args:
        userUUID (str): Target users's UUID. Refer to the doc
        userToken (str): Target users's Token. Refer to the doc

    Returns:
        userInfo (dict | None): The users's informations, or None if an error occurred. Refer to the doc
    """
    userInfo = users.GetUserInfo(userUUID, userToken)
    if userInfo == None:
        return None

    return userInfo

def SubmitBasket(userUUID: str, basketUUID: str, firstName: str, lastName: str, phoneNumber: str, email: str, recaptchaToken: str, userToken: str=None) -> Optional[dict]:
    """
    Create an order by submitting the basket associated with the account.

    This function acts as a wrapper around the corresponding API endpoint.

    Args:
        userUUID (str): Target users's UUID. Refer to the doc
        userToken (str): Target users's Token. Refer to the doc
        basketUUID (str): Target basket's UUID. Refer to the doc
        firstName (str): User's firstname.
        lastName (str): User's lastname.
        phoneNumber (str): User's phoneNumber.
        email (str): User's email.
        recaptchaToken (str): A ReCaptcha Token. Refer to the doc

    Returns:
        orderInfo (dict | None): Informations about the created order, or None if an error occurred. Refer to the doc
    """
    orderInfo = users.RegisterBasket(userUUID, basketUUID, firstName, lastName, phoneNumber, email, recaptchaToken, userToken)
    if orderInfo == None:
        return None

    return orderInfo

def SendUILog(message: str, userToken: str=None) -> Optional[int]:
    """
    Sending UI log message.

    This function acts as a wrapper around the corresponding API endpoint.

    Args:
        message (str): The log message. Refer to the doc
        userToken (str): Target users's Token. Refer to the doc

    Returns:
        orderInfo (dict | None): The request's status code, or None if an error occurred.
    """
    c = users.SendUILog(message, userToken)
    if c == None:
        return None

    return c