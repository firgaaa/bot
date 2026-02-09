"""
Création de comptes KFC France (inscription automatisée).

- Exécution en script : python creation_log.py
- Appel depuis le bot :
    from creation_log import create_account
    result = await create_account()
    if result["ok"]:
        account = result["account"]  # id, mail, password, name1, name2, num, ddn, ...
    else:
        error_msg = result.get("message", result["error"])
"""
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


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG_PATH = os.path.join(SCRIPT_DIR, "error_log.txt")

# Semaphore pour limiter les appels simultanés à reCAPTCHA
_recaptcha_semaphore = None

def init_signup_semaphore(limit=10):
    """Initialise le semaphore pour limiter les appels simultanés à reCAPTCHA."""
    global _recaptcha_semaphore
    _recaptcha_semaphore = asyncio.Semaphore(limit)

def _log_error(error_type, error_msg, context="signup"):
    """Écrit dans error_log.txt (même format que MAIN_CHECK)."""
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(ERROR_LOG_PATH, "a", encoding="utf-8", errors="ignore") as f:
            f.write(f"[{ts}] [{error_type}] {context} - {error_msg}\n")
    except Exception:
        pass


bg = "!q62grYxHRvVxjUIjSFNd0mlvrZ-iCgIHAAAB6FcAAAANnAkBySdqTJGFRK7SirleWAwPVhv9-XwP8ugGSTJJgQ46-0IMBKN8HUnfPqm4sCefwxOOEURND35prc9DJYG0pbmg_jD18qC0c-lQzuPsOtUhHTtfv3--SVCcRvJWZ0V3cia65HGfUys0e1K-IZoArlxM9qZfUMXJKAFuWqZiBn-Qi8VnDqI2rRnAQcIB8Wra6xWzmFbRR2NZqF7lDPKZ0_SZBEc99_49j07ISW4X65sMHL139EARIOipdsj5js5JyM19a2TCZJtAu4XL1h0ZLfomM8KDHkcl_b0L-jW9cvAe2K2uQXKRPzruAvtjdhMdODzVWU5VawKhpmi2NCKAiCRUlJW5lToYkR_X-07AqFLY6qi4ZbJ_sSrD7fCNNYFKmLfAaxPwPmp5Dgei7KKvEQmeUEZwTQAS1p2gaBmt6SCOgId3QBfF_robIkJMcXFzj7R0G-s8rwGUSc8EQzT_DCe9SZsJyobu3Ps0-YK-W3MPWk6a69o618zPSIIQtSCor9w_oUYTLiptaBAEY03NWINhc1mmiYu2Yz5apkW_KbAp3HD3G0bhzcCIYZOGZxyJ44HdGsCJ-7ZFTcEAUST-aLbS-YN1AyuC7ClFO86CMICVDg6aIDyCJyIcaJXiN-bN5xQD_NixaXatJy9Mx1XEnU4Q7E_KISDJfKUhDktK5LMqBJa-x1EIOcY99E-eyry7crf3-Hax3Uj-e-euzRwLxn2VB1Uki8nqJQVYUgcjlVXQhj1X7tx4jzUb0yB1TPU9uMBtZLRvMCRKvFdnn77HgYs5bwOo2mRECiFButgigKXaaJup6NM4KRUevhaDtnD6aJ8ZWQZTXz_OJ74a_OvPK9eD1_5pTG2tUyYNSyz-alhvHdMt5_MAdI3op4ZmcvBQBV9VC2JLjphDuTW8eW_nuK9hN17zin6vjEL8YIm_MekB_dIUK3T1Nbyqmyzigy-Lg8tRL6jSinzdwOTc9hS5SCsPjMeiblc65aJC8AKmA5i80f-6Eg4BT305UeXKI3QwhI3ZJyyQAJTata41FoOXl3EF9Pyy8diYFK2G-CS8lxEpV7jcRYduz4tEPeCpBxU4O_KtM2iv4STkwO4Z_-c-fMLlYu9H7jiFnk6Yh8XlPE__3q0FHIBFf15zVSZ3qroshYiHBMxM5BVQBOExbjoEdYKx4-m9c23K3suA2sCkxHytptG-6yhHJR3EyWwSRTY7OpX_yvhbFri0vgchw7U6ujyoXeCXS9N4oOoGYpS5OyFyRPLxJH7yjXOG2Play5HJ91LL6J6qg1iY8MIq9XQtiVZHadVpZVlz3iKcX4vXcQ3rv_qQwhntObGXPAGJWEel5OiJ1App7mWy961q3mPg9aDEp9VLKU5yDDw1xf6tOFMwg2Q-PNDaKXAyP_FOkxOjnu8dPhuKGut6cJr449BKDwbnA9BOomcVSztEzHGU6HPXXyNdZbfA6D12f5lWxX2B_pobw3a1gFLnO6mWaNRuK1zfzZcfGTYMATf6d7sj9RcKNS230XPHWGaMlLmNxsgXkEN7a9PwsSVwcKdHg_HU4vYdRX6vkEauOIwVPs4dS7yZXmtvbDaX1zOU4ZYWg0T42sT3nIIl9M2EeFS5Rqms_YzNp8J-YtRz1h5RhtTTNcA5jX4N-xDEVx-vD36bZVzfoMSL2k85PKv7pQGLH-0a3DsR0pePCTBWNORK0g_RZCU_H898-nT1syGzNKWGoPCstWPRvpL9cnHRPM1ZKemRn0nPVm9Bgo0ksuUijgXc5yyrf5K49UU2J5JgFYpSp7aMGOUb1ibrj2sr-D63d61DtzFJ2mwrLm_KHBiN_ECpVhDsRvHe5iOx_APHtImevOUxghtkj-8RJruPgkTVaML2MEDOdL_UYaldeo-5ckZo3VHss7IpLArGOMTEd0bSH8tA8CL8RLQQeSokOMZ79Haxj8yE0EAVZ-k9-O72mmu5I0wH5IPgapNvExeX6O1l3mC4MqLhKPdOZOnTiEBlSrV4ZDH_9fhLUahe5ocZXvXqrud9QGNeTpZsSPeIYubeOC0sOsuqk10sWB7NP-lhifWeDob-IK1JWcgFTytVc99RkZTjUcdG9t8prPlKAagZIsDr1TiX3dy8sXKZ7d9EXQF5P_rHJ8xvmUtCWqbc3V5jL-qe8ANypwHsuva75Q6dtqoBR8vCE5xWgfwB0GzR3Xi_l7KDTsYAQIrDZVyY1UxdzWBwJCrvDrtrNsnt0S7BhBJ4ATCrW5VFPqXyXRiLxHCIv9zgo-NdBZQ4hEXXxMtbem3KgYUB1Rals1bbi8X8MsmselnHfY5LdOseyXWIR2QcrANSAypQUAhwVpsModw7HMdXgV9Uc-HwCMWafOChhBr88tOowqVHttPtwYorYrzriXNRt9LkigESMy1bEDx79CJguitwjQ9IyIEu8quEQb_-7AEXrfDzl_FKgASnnZLrAfZMtgyyddIhBpgAvgR_c8a8Nuro-RGV0aNuunVg8NjL8binz9kgmZvOS38QaP5anf2vgzJ9wC0ZKDg2Ad77dPjBCiCRtVe_dqm7FDA_cS97DkAwVfFawgce1wfWqsrjZvu4k6x3PAUH1UNzQUxVgOGUbqJsaFs3GZIMiI8O6-tZktz8i8oqpr0RjkfUhw_I2szHF3LM20_bFwhtINwg0rZxRTrg4il-_q7jDnVOTqQ7fdgHgiJHZw_OOB7JWoRW6ZlJmx3La8oV93fl1wMGNrpojSR0b6pc8SThsKCUgoY6zajWWa3CesX1ZLUtE7Pfk9eDey3stIWf2acKolZ9fU-gspeACUCN20EhGT-HvBtNBGr_xWk1zVJBgNG29olXCpF26eXNKNCCovsILNDgH06vulDUG_vR5RrGe5LsXksIoTMYsCUitLz4HEehUOd9mWCmLCl00eGRCkwr9EB557lyr7mBK2KPgJkXhNmmPSbDy6hPaQ057zfAd5s_43UBCMtI-aAs5NN4TXHd6IlLwynwc1zsYOQ6z_HARlcMpCV9ac-8eOKsaepgjOAX4YHfg3NekrxA2ynrvwk9U-gCtpxMJ4f1cVx3jExNlIX5LxE46FYIhQ"
RECAPTCHA_URL_GET = "https://recaptcha.net/recaptcha/api2/anchor?ar=2&k=6LdkEnMaAAAAAJdHrWw86-qry-pB2LYDbaDYirJs&co=aHR0cHM6Ly93d3cua2ZjLmZyOjQ0Mw..&hl=fr&v=7gg7H51Q-naNfhmCP3_R47ho&size=invisible&anchor-ms=20000&execute-ms=30000&cb=dzm7xesp46th"
RECAPTCHA_URL_POST = "https://recaptcha.net/recaptcha/api2/reload?k=6LdkEnMaAAAAAJdHrWw86-qry-pB2LYDbaDYirJs"
REFERER = ""
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    

# Liste exhaustive de prénoms français
prenoms = ["Liam","Noah","Gabriel","Adam","Lucas","Hugo","Nathan","Ethan","Sacha","Leo",
    "Milo","Jules","Mael","Raphael","Aaron","Nael","Tiago","Louis","Paul","Arthur",
    "Tom","Nino","Mathis","Elio","Noe","Theo","Axel","Evan","Yanis","Sami",
    "Isaac","Oscar","Marin","Tao","Eden","Nolan","Ayden","Amir","Ilyes","Loan",
    "Soan","Kylian","Timeo","Mae","Kayden","Rayan","Alessio","Matheo","Elian","Kais",
    "Ilan","Noam","Elias","Côme","Esteban","Marius","Soren","Lenny","Andrea","Célian",
    "Mathéo","Aylan","Adem","Wassim","Imran","Mika","Alec","Enzo","Valentin","Basile",
    "Emma","Jade","Lou","Alice","Lina","Mila","Rose","Chloe","Lea","Inaya",
    "Anna","Zoe","Mia","Iris","Ambre","Romy","Juliette","Alma","Nina","Eva",
    "Louna","Camille","Sarah","Elena","Lila","Olivia","Lena","Aya","Yasmine","Lyana",
    "Elsa","Manon","Celia","Sofia","Maelys","Nour","Victoria","Agathe","Adele","Clara",
    "Soline","Giulia","Melina","Charlie","Lola","Noa","Elina","Emy","Talia","Livia",
    "Alya","Kiara","Melia","Ilona","Lana","Emmy","Maia","Zelie","Thais","Lior",
    "Elora","Naomie","Amaya","Kayla","Liyana","Assia","Mayssa","Elise","Ines","Maeva",
    "Salome","Hanae","Lise","Yuna","Kenza","Melissa","Apolline","Margot","Capucine","Amandine",
    "Thea","Leya","Anya","Liorah","Sasha","Liyana","Mina","Cassi","Elowen","Ariane",
    "Noemie","Anouk","Liviah","Maureen","Lylou","Lenaelle","Romane","Elya","Cloe","Anae",
    "Isis","Livia","Celeste","Lison","Yse","Lorie","Elia","Maissa","Aliya","Sirine"
]

# Liste exhaustive de noms de famille français
noms = ["Valmorin","Delraye","Montelis","Bravoux","Sorelli","Tervain","Lunaret","Corsinac","Belvior","Darmelis",
    "Rovelin","Marceval","Torvani","Lazurel","Viremont","Caldris","Montara","Selvane","Brunelac","Dorvian",
    "Velmori","Castelin","Norvane","Albrion","Mercelis","Durvale","Solvian","Carmelis","Dorevain","Lunebrac",
    "Marvaux","Torelian","Belmire","Savorel","Montelis","Ravellec","Cendral","Valeris","Morvani","Serdane",
    "Brivelac","Orliane","Delmoris","Varnel","Sorvani","Calvirex","Mirelune","Dorselin","Valdorin","Lestari",
    "Bracelin","Corvane","Mireval","Solvane","Tervaux","Lunaris","Montelac","Belvane","Rovaire","Carmorin",
    "Velaris","Dalmire","Norvain","Selvaris","Brumelis","Torvain","Lacorin","Merelis","Virelan","Sorvain",
    "Calvane","Doralis","Marvane","Lunovar","Belaris","Montorin","Serelis","Valmarex","Corliane","Ravarin",
    "Delvane","Briselor","Toralis","Cendrine","Morvane","Velorin","Soreline","Lunavex","Montelis","Carvane",
    "Dorelis","Selmara","Bravane","Valeris","Orvalen","Noralis","Merovian","Tervalin","Belvaris","Calmirex",
    "Sorvalis","Lunaris","Montarel","Rovelin","Velmara","Corvain","Delaris","Briselin","Morvalis","Selvarin",
    "Torvane","Carmelin","Valorin","Lunelis","Norvane","Belmoris","Dalmorin","Serliane","Bravorel","Montelir",
    "Velorin","Raveline","Calvorel","Sorvanel","Delmara","Corvalin","Lunaris","Merelian","Torvalis","Belorin",
    "Montaris","Selvorel","Brisane","Valdorel","Norvane","Carvalis","Doreval","Lunaris","Morvanel","Velaris",
    "Sorline","Delvorel","Briselac","Torvorel","Calvarin","Montelane","Belvarin","Rovelis","Selmoris","Carmorel",
    "Valeris","Norvorel","Lunaris","Morvalin","Seravane","Bravorel","Delmaris","Torvalin","Belmara","Calvanel",
    "Sorvorel","Velmoris","Montelir","Ravanel","Corvorel","Lunaris","Valmarel","Selvaris","Dorelin","Briselor",
    "Torvanel","Carvorel","Norvalis","Montelis","Belvorel","Delvarin","Soranel","Velmarex","Calvorel","Morvane",
    "Lunaris","Seranel","Bravanel","Valdorin","Torvorel","Carmaris","Selvanel","Montaril","Belvaris","Delmoris"
    "Aurevane","Belcrion","Carmelune","Dorsavian","Elvaris","Fernelac","Gavorel","Harmelin","Isvalen","Jorvane",
    "Kelmaris","Lunaviel","Morvanelis","Norvirex","Ormelian","Perliane","Quervalis","Ravemont","Selvarion","Torvanelis",
    "Ulmarin","Valcriane","Wervalin","Xandorel","Ysmarel","Zorvanel","Alverion","Brumarel","Cendralis","Dorvalen",
    "Esmorian","Falvirex","Germalune","Helvaris","Irmarel","Jarvelin","Korvanel","Lormaris","Mirevalen","Nervalion",
    "Orvirel","Parmelis","Quelvarin","Rismarel","Solvaris","Tormelin","Urvalis","Vermalion","Wandorel","Xermaris",
    "Yorvalen","Zelmorin","Arvanelis","Belmorian","Corvalune","Delvaris","Elmorane","Fervalin","Gormelis","Hervanel",
    "Ismorian","Jalveris","Kelvanel","Larmelis","Marvirel","Norvalune","Orvanelis","Pervalin","Quelmoris","Ravanelis",
    "Selvarune","Torvaline","Ulveranis","Valmorian","Wermelis","Xorvalis","Yervanel","Zorvalune","Almirelis","Bravanelis",
    "Cervalin","Dalmorane","Erlavine","Falmoris","Gorvanelis","Helmorian","Irvalune","Jormelis","Korvaline","Lervanis",
    "Mormelis","Nalmorian","Orvaline","Parvanel","Quorvalis","Ralmorian","Servanelis","Tervaline","Ulmanelis","Vormaris",
    "Walmorian","Xelvanel","Yalmoris","Zervaline","Alvirelis","Belvarune","Corvanelis","Delmorian","Elvarune","Falvanelis",
    "Gervaline","Helvanelis","Irmanelis","Jarvanelis","Kelvarune","Lomarelis","Morvalune","Norvanelis","Ormarelis","Pervalune",
    "Quermanelis","Rovarelis","Selmarelis","Torvarelis","Ulmarelis","Valmarelis","Wermarelis","Xormarelis","Yormarelis","Zormarelis",
    "Alvaranel","Belvaranel","Corvaranel","Delvaranel","Elvaranel","Falvaranel","Garvaranel","Helvaranel","Irvaranel","Jarvaranel",
    "Kelvaranel","Larvaranel","Morvaranel","Norvaranel","Orvaranel","Parvaranel","Quarvaranel","Rarvaranel","Sarvaranel","Tarvaranel",
    "Ulvaranel","Varvaranel","Warvaranel","Xarvaranel","Yarvaranel","Zarvaranel","Almoriane","Belmoriane","Cormoriane","Delmoriane",
    "Elmoriane","Falmoriane","Galmoriane","Helmoriane","Irmoriane","Jormoriane","Kelmoriane","Lelmoriane","Mormoriane","Normoriane",
    "Ormoriane","Parmoriane","Quelmoriane","Ralmoriane","Selmoriane","Telmoriane","Ulmoriane","Valmoriane","Welmoriane","Xelmoriane",
    "Yelmoriane","Zelmoriane","Alvarionis","Belvarionis","Corvarionis","Delvarionis","Elvarionis","Falvarionis","Garvarionis","Helvarionis",
    "Irvarionis","Jarvarionis","Kelvarionis","Larvarionis","Morvarionis","Norvarionis","Orvarionis","Parvarionis","Quarvarionis","Rarvarionis"
    ]

domain_liste = ["yopmail.com","noopmail"]

noop_liste = ["yomand.store","pushcom.store","nooploop.store","mailnoop.store","mynoop.store","meomo.store","sihanoma.store","taohucom.store","20minutesmail.com","colurmish.com","muetop.store","magbit.food","mongrec.top","kokalo.store","nhoopmail.store","iuanhoi.store","pricegh.fun","ihnpo.food","hooooooo.store","eligou.store","temppppo.store","xopmail.fun","cood.food","noopmail.com"]





async def generer_date_naissance():
    # Date de début : 1er janvier 1980
    date_debut = datetime(1980, 1, 1)
    # Date de fin : 31 décembre 2005
    date_fin = datetime(2005, 12, 31)
    
    # Calculer le nombre de jours entre les deux dates
    delta = date_fin - date_debut
    jours_aleatoires = random.randint(0, delta.days)
    
    # Générer la date aléatoire
    date_aleatoire = date_debut + timedelta(days=jours_aleatoires)
    
    return date_aleatoire.day, date_aleatoire.month, date_aleatoire.year, date_aleatoire.strftime("%Y-%m-%dT00:00:00.000Z")

async def generer_nom_prenom():
    prenom_aleatoire = random.choice(prenoms)
    #prenom_aleatoire = "Jed"
    nom_aleatoire = random.choice(noms)
    
    return prenom_aleatoire, nom_aleatoire

async def bypass_recaptcha_v3(recaptcha_url_get, recaptcha_url_post, referer, user_agent, bg):
    """
    Bypass reCAPTCHA v3 et retourne le token rresp
    
    Args:
        recaptcha_url_get: URL pour la requête GET (anchor)
        recaptcha_url_post: URL pour la requête POST (reload)
        referer: Referer header
        user_agent: User-Agent string
        bg: Paramètre BG (longue chaîne encodée)
    
    Returns:
        str: Token rresp ou None en cas d'erreur
    """
    
    # Utiliser le semaphore pour limiter les appels simultanés
    if _recaptcha_semaphore is None:
        init_signup_semaphore(10)  # Valeur par défaut si non initialisé
    
    async with _recaptcha_semaphore:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        try:
            async with aiohttp.ClientSession() as session:
                # ===== ÉTAPE 1: Requête GET =====
                headers_get = {
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate",
                    "Upgrade-Insecure-Requests": "1",
                    "Connection": "keep-alive"
                }
                
                async with session.get(recaptcha_url_get, headers=headers_get, ssl=ssl_context) as response_get:
                    if response_get.status != 200:
                        _log_error("recaptcha_get", f"GET {response_get.status}", "recaptcha")
                        print(f" Erreur GET: {response_get.status}")
                        return None
                    
                    text_get = await response_get.text()
                    
                    # Extraire le token caché
                    match_token = re.search(r'id="recaptcha-token" value="(.*?)"', text_get)
                    if not match_token:
                        _log_error("recaptcha_token", "Token recaptcha-token introuvable", "recaptcha")
                        print(" Token recaptcha-token introuvable")
                        return None
                    
                    recaptcha_token = match_token.group(1)
                    
                    # Extraire les paramètres de l'URL GET
                    match_v = re.search(r'v=(.*?)&', recaptcha_url_get)
                    match_k = re.search(r'&k=(.*?)&', recaptcha_url_get)
                    match_co = re.search(r'&co=(.*?)&', recaptcha_url_get)
                    
                    if not (match_v and match_k and match_co):
                        _log_error("recaptcha_params", "v, k ou co non trouvés [ l'URL GET ]", "recaptcha")
                        print("v, k ou co non trouvés [ l'URL GET ]")
                        return None
                    
                    v = match_v.group(1)
                    k = match_k.group(1)
                    co = match_co.group(1)
                    
                    # ===== ÉTAPE 2: Requête POST =====
                    post_data = f"v={v}&reason=q&c={recaptcha_token}&k={k}&co={co}&hl=en&size=invisible&chr=%5B89%2C64%2C27%5D&vh=13599012192&bg={bg}"
                    
                    headers_post = {
                        "User-Agent": user_agent,
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "fa,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
                        "Content-Length": str(len(post_data)),
                        "Connection": "keep-alive",
                        "Origin": "https://www.google.com",
                        "Referer": referer if referer else recaptcha_url_get,
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                    
                    async with session.post(recaptcha_url_post, data=post_data, headers=headers_post, ssl=ssl_context) as response_post:
                        if response_post.status != 200:
                            _log_error("recaptcha_post", f"POST {response_post.status}", "recaptcha")
                            print(f" Erreur POST: {response_post.status}")
                            return None
                        
                        text_post = await response_post.text()
                        
                        # Extraire le rresp
                        match_rresp = re.search(r'"rresp","(.*?)"', text_post)
                        if not match_rresp:
                            _log_error("recaptcha_rresp", f"Réponse: {text_post[:200]}", "recaptcha")
                            print(f"Réponse: {text_post[:200]}")
                            return None
                        
                        rresp = match_rresp.group(1)
                        #print(f"rresp : {rresp[:50]}...")
                        
                        return rresp
            
        except Exception as e:
            _log_error("recaptcha_exception", str(e)[:200], "recaptcha")
            print(f" Erreur: {e}")
            return None

def generate_mail():
    length = 10
    characters = string.ascii_letters + string.digits
    local_part = ''.join(random.choice(characters) for _ in range(length))
    
    domain = random.choice(domain_liste)
    if domain == "noopmail":
        domain = random.choice(noop_liste)
    
    return f"{local_part}@{domain}"

def generate_numero():
    length = 8
    characters = string.digits
    numero = ''.join(random.choice(characters) for _ in range(length))
    
    
    return '07' + numero

def generate_password(length=12):
    if length < 8:
        raise ValueError("La longueur minimale pour un mot de passe est de 8 caractères.")

    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "#.$@!%*?"
    all_chars = lowercase + uppercase + digits + special_chars

    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special_chars)
    ]

    password += random.choices(all_chars, k=length - 4)

    random.shuffle(password)

    return ''.join(password)













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




def encrypt(first_name, last_name, email, password, phone, recaptcha_token, dob="1998-02-01T00:00:00.000Z", 
             marketing_opt_in=False):
    aes_key = generate_key()
    data = {
        "firstName": encrypt_aes(first_name, aes_key),
        "lastName": encrypt_aes(last_name, aes_key),
        "email": encrypt_aes(email, aes_key),
        "password": encrypt_aes(password, aes_key),
        "phoneNumber": encrypt_aes(phone, aes_key),
        "marketingOptIn": marketing_opt_in,
        "subscribeChannel": [0, 0],
        "recaptchaToken": recaptcha_token,
        "dob": dob,
        "acceptTermConditions": True,
        "RegisterChannelType": "Desktop Browser"
    }
    
    # ← CORRECTION ICI : separators=(',', ':') pour enlever les espaces
    return json.dumps({
        "data": encrypt_aes(json.dumps(data, separators=(',', ':')), aes_key),
        "key": encrypt_rsa(aes_key)
    }, separators=(',', ':'))

async def send_signup(payload, context="signup"):

    PROXY = {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080"  # ← Ajouter aussi HTTP
    }
    
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    timeout = aiohttp.ClientTimeout(total=20)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "https://13.248.197.133/api/register",
                data=payload,
                headers={
                    "Host": "13.248.197.133",
                    "Content-Length": str(len(payload)), 
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Accept-Language": "fr-FR,fr;q=0.9",
                    "Sec-Ch-Ua": '"Chromium";v="143", "Not A(Brand";v="24"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Culturecode": "fr",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                    "Origin": "https://www.kfc.fr",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "https://www.kfc.fr/mon-compte/inscription",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Priority": "u=1, i"
                },
                #proxy=PROXY.get("https"),
                ssl=ssl_context
            ) as reponse:
                text_response = await reponse.text()
                
                if reponse.status == 400:
                    _log_error("signup_400", (text_response or "")[:200], context)
                    print(f"{Fore.RED}{reponse.status}", f"{Fore.RESET}{text_response}\n")
                    return "erreur", text_response
    
                elif "éjà enregistré, merci d’en saisir un autre" in text_response:
                    _log_error("signup_email_taken", "Email déjà enregistré, merci d'en saisir un autre", context)
                    print(f"{Fore.YELLOW}{reponse.status}", f"{Fore.RESET}{text_response}\n")
                    return "erreur", text_response

                else:
                    print(f"{Fore.GREEN}{reponse.status}", f"{Fore.RESET}{text_response}\n")
                    try:
                        data = json.loads(text_response)
                    except json.JSONDecodeError:
                        _log_error("signup_json", f"Parse JSON échoué: {text_response[:200]}", context)
                        return "erreur", text_response
                    return "success", data
    
    except Exception as e:
        _log_error("signup_exception", str(e)[:200], context)
        print(f"{Fore.RED}Erreur dans send_signup: {e}{Fore.RESET}")
        return "erreur", str(e)



async def signup():
    name1, name2 = await generer_nom_prenom()
    jour, mois, annee, ddn = await generer_date_naissance()
    mail = generate_mail()
    password = generate_password(9)
    num = generate_numero()
    
    token = await bypass_recaptcha_v3(
        recaptcha_url_get=RECAPTCHA_URL_GET,
        recaptcha_url_post=RECAPTCHA_URL_POST,
        referer=REFERER,
        user_agent=USER_AGENT,
        bg=bg
    )
    
    if not token:
        _log_error("signup_recaptcha", "Token reCAPTCHA non obtenu", mail)
        return "erreur"
    
    payload = encrypt(name1,
                    name2,
                    mail, 
                    password, 
                    num, 
                    token,
                    ddn
                    )
    
    statut, rep = await send_signup(payload, context=mail)
    if statut == "success":
        id = rep.get("user", {}).get("id")

        result = {
            "id": id,
            "name1": name1,
            "name2": name2,
            "mail": mail, 
            "password": password, 
            "num": num, 
            "ddn": ddn,
            "jour": jour,
            "mois": mois,
            "annee": annee
            }
    else:
        return "erreur"
    
    return result


# ---------------------------------------------------------------------------
# API publique pour le bot : un seul point d'entrée, retour structuré
# ---------------------------------------------------------------------------

def _ensure_semaphore():
    """Initialise le sémaphore reCAPTCHA au premier usage (import ou premier appel)."""
    global _recaptcha_semaphore
    if _recaptcha_semaphore is None:
        init_signup_semaphore(10)


async def create_account():
    """
    Crée un compte KFC (données aléatoires, bypass reCAPTCHA, appel API).
    À utiliser depuis le bot ou tout code async.

    Returns:
        dict: En succès : {"ok": True, "account": {"id", "mail", "password", "name1", "name2", "num", "ddn", ...}}
              En échec : {"ok": False, "error": "<code>", "message": "<texte pour l'utilisateur>"}
    """
    _ensure_semaphore()
    result = await signup()
    if result == "erreur":
        return {
            "ok": False,
            "error": "creation_failed",
            "message": "Échec de la création du compte (reCAPTCHA ou API). Consultez error_log.txt si besoin.",
        }
    return {"ok": True, "account": result}


# Initialisation au chargement du module (prêt pour le bot)
_ensure_semaphore()


if __name__ == "__main__":
    try:
        init()
    except Exception:
        pass

    async def _main():
        print("Création d'un compte KFC en cours...")
        r = await create_account()
        if r.get("ok"):
            acc = r["account"]
            print(f"Compte créé : {acc.get('mail')} / id={acc.get('id')}")
        else:
            print(f"Erreur : {r.get('message', r.get('error'))}")

    asyncio.run(_main())
