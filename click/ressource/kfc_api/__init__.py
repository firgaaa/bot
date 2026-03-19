import uuid

BRAZE_APIKEY = "a2efe7e4-929c-43f5-a085-7df8358ad687"
BRAZE_SESSIONID = str(uuid.uuid4()) #random
BRAZE_DEVICEID = str(uuid.uuid4()) #random
BRAZE_USERAPPID = "de0ffe3a8968a28d0ef14590a9631ad4761c1c78eb472521fd9389254c783cd1" #random ?

COOKIES = {
    ".AspNetCore.Antiforgery.OWt5i9qH0oM": "CfDJ8I9zZrDeBTtGjN412kp4Vld32Is3L297pNzOz8OnGdYZuELsmb752MGZPnhqdyX4bPnC9jWJg_rSfNotdDQScTMJ5skiZnWd8Ioh-_isgVwkytZwyaz7_P6-v6kO1LwOctPbgzg5fk1DSJzzrnidlQ8",
    "XSRF-TOKEN": "CfDJ8I9zZrDeBTtGjN412kp4Vlehsc_h6AMvdFOzkdGYJyKXWN6mPad0A8tHALcw_c3YKesiG0x9WXZ71TYbRApQcAjVLvoVdbZiomM9nyyRSOO55c-iTpyPtqIaB6i1yrqLiracu3amoAHICuKRcv6N3kU",
    "refreshToken": "p3g880b3q+IXhdyPmdVSvr5oLyYizN0lnLZVRgzce0dqYa2Gc5D/P74NGrup7qX+k1wTiq8ltHM2h6zKRhdtGg==",
}

"""
All the files in this modules are direct requests to the api.
I don't recommend using them, you should instead use the Wrapper in the parent folder.
"""