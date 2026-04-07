
import json
import base64
import random
import aiohttp
import ssl
import string
import re
import os
import time
from colorama import Fore, init
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
import asyncio
from datetime import datetime, timedelta

# Configuration
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----\n  MIGeMA0GCSqGSIb3DQEBAQUAA4GMADCBiAKBgHO4AqKut5xbco9jgfz+bqkx9v0M\nO9t5DGzZEltqqZE5tNzHbve2D+KPWTeD+G9q2PilkPPHRz2+r5MgwlD4dGP6zum3\nhNj27CCIgUeaIJGhX/JlmBO3bgFGCcuemuKc+ygFJYvf0RzCo5svfn/6cKSHeovl\norMqQbQU3GrHLVA9AgMBAAE=\n  -----END PUBLIC KEY-----"""
IV = "@qwertyuiop12344"

def generate_key():
    chars = "@abcdefghijklmnopqrstuvwxyz123456789"
    return ''.join(random.choice(chars) for _ in range(16))

def encrypt_aes(text, key):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, IV.encode('utf-8'))
    padded = pad(text.encode('utf-8'), AES.block_size)
    return base64.b64encode(cipher.encrypt(padded)).decode('utf-8')

def encrypt_rsa(text):
    rsa_key = RSA.import_key(PUBLIC_KEY)
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypted = cipher.encrypt(text.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')

"""
def login(email, password):
    aes_key = generate_key()
    data = {
        "email": encrypt_aes(email, aes_key),
        "password": encrypt_aes(password, aes_key)
    }
    return json.dumps({
        "data": encrypt_aes(json.dumps(data), aes_key),
        "key": encrypt_rsa(aes_key)
    })
"""




def encrypt(email, password):
    aes_key = generate_key()
    data = {
        "email": encrypt_aes(email, aes_key),
        "password": encrypt_aes(password, aes_key),
    }
    
    # ← CORRECTION ICI : separators=(',', ':') pour enlever les espaces
    return json.dumps({
        "data": encrypt_aes(json.dumps(data, separators=(',', ':')), aes_key),
        "key": encrypt_rsa(aes_key)
    }, separators=(',', ':'))







mail = "lw90ehlgpr@xitroo.fr"
password = "HoJ26It?P"

    
payload = encrypt(
            mail, 
            password
            )
    
print(payload)
