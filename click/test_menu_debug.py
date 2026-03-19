"""
Script de test pour inspecter la structure du menu fidélité (modgrps).
À exécuter depuis le dossier click/ :  python test_menu_debug.py

Permet de vérifier si les items menu (ex. Kentucky® BBQ & Bacon) ont bien
des modgrps imbriqués (boisson, accompagnement) et de tester des solutions
avant de les adapter dans le bot.

À faire avant de lancer :
  - Remplacer ACCOUNT_ID et ACCOUNT_TOKEN par tes vraies valeurs (ne pas commiter).
  - Optionnel : ajouter test_menu_dump.json au .gitignore si tu sauvegardes le dump.
"""
import json
import os
import sys
from pathlib import Path

# S'assurer d'exécuter depuis le dossier click/ pour les imports
CLICK_DIR = Path(__file__).resolve().parent
os.chdir(CLICK_DIR)
if str(CLICK_DIR) not in sys.path:
    sys.path.insert(0, str(CLICK_DIR))

# --- Constantes de test (à remplir avec tes valeurs) ---
ACCOUNT_ID = "c1f3eda7-63cd-47d0-be9d-c3934fcc9b7a"
ACCOUNT_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NzMxMDM3OTQsIklkIjoiYzFmM2VkYTctNjNjZC00N2QwLWJlOWQtYzM5MzRmY2M5YjdhIiwiRmlyc3ROYW1lIjoiYWxhbGxhIiwiTGFzdE5hbWUiOiJsYWxhbGFsIiwiRW1haWwiOiJhbGFsbGEucGVyc29vb0BnbWFpbC5jb20iLCJuYmYiOjE3NzMxMDM3OTQsImV4cCI6MTc4MDg3OTc5NCwiaXNzIjoiTWUiLCJhdWQiOiJ5b3UifQ.GumbjA2Sr5Lht6x9fwVpzYYYncVABaCGi4T_dLeWzDMu6vNMEZsb3GuyMhl2Wz5xR_TPcLXFJ_2piAk70-oa7HrJ7uIHgqhKEY8GgNwvgUb5Nt_wsHRYII7p0HCOCC3oV1Vfga1WkFzQBQa0i0N-3fKxMHiATxsQWHth8H46ud_P_pIMQJmYdx6o-ZgnDQ_NXVrPW1ndiKUXTvxn4MN2xdKoG2Z9Y5vsGxXnNqOT-gscg-vpDccsFXl9I1nsY01_MOGaDPAJr3VhgJwWIrMG-6cuJbDetOvIKf60bPv3to5aXae2VCnwyBBuqxU_ZckG5_EQrkt_GITrGxE3Q7crew"
STORE_ID = "79075021"  # ex. Montevrain

# Fichier de sortie pour dump complet (optionnel)
OUTPUT_JSON = CLICK_DIR / "test_menu_dump.json"


# --- Logique v2 (copie locale pour comparaison) ---
def _build_modifier_v2(node):
    """Copie de v2: utilise node['price'] uniquement (pas posPrice)."""
    unit_price = node.get("price", node.get("posPrice", 0))
    if unit_price is None:
        unit_price = 0
    modifier = {
        "id": node["id"],
        "unitPrice": unit_price,
        "quantity": node.get("qty", 0),
    }
    if node.get("modgrps"):
        modifier["modgrps"] = [_build_modgrp_v2(mg) for mg in node["modgrps"]]
    return modifier


def _build_modgrp_v2(group):
    """Copie de v2: build_modgrp."""
    return {
        "id": group["id"],
        "modifiers": [
            _build_modifier_v2(mod) for mod in group.get("modifiers", []) if mod.get("qty", 0) > 0
        ],
    }


def _fill_tree_first_choice(tree):
    """
    Remplit l'arbre comme le bot / v2 en simulant "toujours premier choix":
    pour chaque groupe, tous les modifiers à 0 puis premier à group['max'], puis récursion dans modgrps.
    Muté en place.
    """
    if not tree:
        return
    for group in tree:
        mods = group.get("modifiers", [])
        if not mods:
            continue
        for m in mods:
            m["qty"] = 0
        mods[0]["qty"] = group.get("max", 1)
        nested = mods[0].get("modgrps") or []
        if nested:
            _fill_tree_first_choice(nested)


def _compare_payloads(payload_bot, payload_v2, item_name):
    """Affiche les différences entre les deux payloads."""
    lines = []
    lines.append(f"   Comparaison pour item: {item_name}")
    lines.append(f"   Nombre de groupes (top-level): BOT={len(payload_bot)}  v2={len(payload_v2)}")
    if len(payload_bot) != len(payload_v2):
        lines.append("   ⚠️  DIFF: nombre de groupes différent!")
    for i, (gb, gv) in enumerate(zip(payload_bot, payload_v2)):
        id_b, id_v = gb.get("id"), gv.get("id")
        mods_b, mods_v = gb.get("modifiers", []), gv.get("modifiers", [])
        if id_b != id_v:
            lines.append(f"   Groupe {i}: id BOT={id_b}  v2={id_v}")
        if len(mods_b) != len(mods_v):
            lines.append(f"   Groupe {i} ({id_b}): modifiers BOT={len(mods_b)}  v2={len(mods_v)}")
        for j, (mb, mv) in enumerate(zip(mods_b, mods_v)):
            if mb.get("id") != mv.get("id"):
                lines.append(f"      Modifier {j}: id BOT={mb.get('id')}  v2={mv.get('id')}")
            if mb.get("unitPrice") != mv.get("unitPrice"):
                lines.append(f"      Modifier {j} ({mb.get('id')}): unitPrice BOT={mb.get('unitPrice')}  v2={mv.get('unitPrice')}")
            if mb.get("quantity") != mv.get("quantity"):
                lines.append(f"      Modifier {j} ({mb.get('id')}): quantity BOT={mb.get('quantity')}  v2={mv.get('quantity')}")
    if len(payload_bot) > len(payload_v2):
        for i in range(len(payload_v2), len(payload_bot)):
            lines.append(f"   Groupe {i} (BOT seul): id={payload_bot[i].get('id')}")
    elif len(payload_v2) > len(payload_bot):
        for i in range(len(payload_bot), len(payload_v2)):
            lines.append(f"   Groupe {i} (v2 seul): id={payload_v2[i].get('id')}")
    return "\n".join(lines)


def main():
    print("=== Test structure menu fidélité ===\n")
    print(f"Store ID: {STORE_ID}")
    print(f"Account ID: {ACCOUNT_ID[:8]}...\n")

    if ACCOUNT_ID == "votre_account_id" or ACCOUNT_TOKEN == "votre_account_token":
        print("⚠️  Modifie ACCOUNT_ID et ACCOUNT_TOKEN en haut du fichier avec tes vraies valeurs.")
        return

    from ressource import loyalty, account
    from ressource.kfc_api import stores

    # 1) Récupérer le menu store (comme preview-menu)
    print("1) GetStoreMenu...")
    store_menu = stores.GetStoreMenu(STORE_ID)
    if store_menu is None:
        print("   ❌ GetStoreMenu a échoué")
        return

    # 2) Catégorie LOYALTY
    print("2) GetLoyaltyFromStore...")
    store_loyalty = loyalty.GetLoyaltyFromStore(STORE_ID)
    if store_loyalty is None:
        print("   ❌ GetLoyaltyFromStore a échoué")
        return

    # 3) Infos compte
    print("3) GetAccountLoyaltyInfo...")
    loyalty_info = account.GetAccountLoyaltyInfo(ACCOUNT_ID, ACCOUNT_TOKEN)
    if loyalty_info is None:
        print("   ❌ GetAccountLoyaltyInfo a échoué")
        return

    rewards = loyalty_info.get("rewards")
    if not rewards:
        print("   ❌ Pas de rewards dans le compte")
        return

    # 4) Menu matché (comme le bot / preview-menu)
    print("4) LoyaltyMatch...")
    menu, matched_count = loyalty.LoyaltyMatch(rewards, store_loyalty)
    print(f"   Items matchés: {matched_count}\n")

    # 5) Inspecter les items avec modgrps
    print("5) Inspection des modgrps par item ---")
    items_with_modgrps = []
    for cat_name, items in menu.items():
        for item in items:
            name = item.get("name", "?")
            modgrps = item.get("modgrps")
            if not modgrps:
                continue
            items_with_modgrps.append((cat_name, name, item))
            print(f"\n   [{cat_name}] {name}")
            print(f"      modgrps: {len(modgrps)} groupe(s) au top-level")
            for gi, group in enumerate(modgrps):
                grp_name = group.get("name", "?")
                modifiers = group.get("modifiers", [])
                print(f"      Groupe {gi}: {grp_name} ({len(modifiers)} modifier(s))")
                for mi, mod in enumerate(modifiers):
                    mod_name = mod.get("name", "?")
                    nested = mod.get("modgrps") or []
                    has_nested = "OUI" if nested else "NON"
                    print(f"         Modifier {mi}: {mod_name} -> modgrps imbriqués: {has_nested} (len={len(nested)})")
                    if nested:
                        for ni, ng in enumerate(nested):
                            print(f"            Nested group {ni}: {ng.get('name', '?')} ({len(ng.get('modifiers', []))} mods)")

    # 6) Dump complet du menu matché (pour analyse)
    if items_with_modgrps:
        dump = {
            "store_id": STORE_ID,
            "matched_count": matched_count,
            "categories": menu,
            "items_with_modgrps_summary": [
                {"category": c, "name": it.get("name"), "id": it.get("id"), "modgrps_count": len(it.get("modgrps", []))}
                for c, n, it in items_with_modgrps
            ],
        }
        try:
            with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                json.dump(dump, f, ensure_ascii=False, indent=2)
            print(f"\n   Dump complet sauvegardé: {OUTPUT_JSON}")
        except Exception as e:
            print(f"\n   Erreur sauvegarde dump: {e}")
    else:
        print("\n   Aucun item avec modgrps trouvé.")

    # 7) Résumé pour Menu Kentucky (ou premier menu avec modgrps)
    print("\n6) Résumé cible (menu type Kentucky / premier avec modgrps) ---")
    for cat_name, name, item in items_with_modgrps:
        if "Kentucky" in name or "Menu" in name or "Tower" in name:
            modgrps = item.get("modgrps", [])
            if modgrps and modgrps[0].get("modifiers"):
                first_mod = modgrps[0]["modifiers"][0]
                nested = first_mod.get("modgrps")
                print(f"   Item: {name}")
                print(f"   Premier modifier a modgrps imbriqués: {'OUI' if nested else 'NON'}")
                if nested:
                    print(f"   Nombre de sous-groupes (ex. boisson, accomp): {len(nested)}")
                break
    else:
        if items_with_modgrps:
            cat_name, name, item = items_with_modgrps[0]
            modgrps = item.get("modgrps", [])
            if modgrps and modgrps[0].get("modifiers"):
                first_mod = modgrps[0]["modifiers"][0]
                nested = first_mod.get("modgrps")
                print(f"   Premier item avec modgrps: {name}")
                print(f"   Premier modifier a modgrps imbriqués: {'OUI' if nested else 'NON'}")

    # 8) Test build_modgrps_from_tree sur un arbre type "menu complet" (burger + boisson + accomp)
    print("\n7) Test build_modgrps_from_tree (arbre type Kentucky rempli) ---")
    from ressource import modgrps as modgrps_module
    import copy as copy_module

    # Arbre minimal : 1 groupe PRODUIT, 1 modifier (burger) avec qty=1 et 2 sous-groupes (boisson, accomp)
    fake_tree = [
        {
            "id": "1",
            "name": "PRODUIT",
            "modifiers": [
                {
                    "id": "3110",
                    "name": "Kentucky® BBQ & Bacon",
                    "price": 0,
                    "posPrice": 0,
                    "qty": 1,
                    "modgrps": [
                        {
                            "id": "boisson",
                            "name": "Boisson",
                            "modifiers": [
                                {"id": "coca", "name": "Coca", "price": 0, "qty": 1},
                            ],
                        },
                        {
                            "id": "accomp",
                            "name": "Accompagnement",
                            "modifiers": [
                                {"id": "frites", "name": "Frites", "price": 0, "qty": 1},
                            ],
                        },
                    ],
                },
            ],
        },
    ]
    built = modgrps_module.build_modgrps_from_tree(fake_tree)
    print("   Arbre test (burger + boisson + accomp) -> payload pour KFC:")
    print(json.dumps(built, ensure_ascii=False, indent=2))
    print("\n   Si tu vois bien 'modgrps' avec Boisson et Accompagnement ci-dessus,")
    print("   le format est correct. Le bot doit produire un arbre rempli comme ça.")

    # 9) Si on a trouvé un vrai item Kentucky avec modgrps imbriqués, tester avec une copie remplie
    for cat_name, name, item in items_with_modgrps:
        if "Kentucky" not in name and "Tower" not in name:
            continue
        modgrps = item.get("modgrps") or []
        if not modgrps or not modgrps[0].get("modifiers"):
            continue
        first_mod = modgrps[0]["modifiers"][0]
        if not first_mod.get("modgrps"):
            continue
        tree_copy = copy_module.deepcopy(modgrps)
        for g in tree_copy:
            for m in g.get("modifiers", []):
                m["qty"] = 0
        tree_copy[0]["modifiers"][0]["qty"] = 1
        nested = tree_copy[0]["modifiers"][0].get("modgrps") or []
        for ng in nested:
            mods = ng.get("modifiers", [])
            if mods:
                mods[0]["qty"] = 1
        built_real = modgrps_module.build_modgrps_from_tree(tree_copy)
        print(f"\n8) Test avec VRAI item '{name}' (arbre rempli manuellement) ---")
        print(json.dumps(built_real, ensure_ascii=False, indent=2))
        break

    # 9) Comparaison BOT vs v2 : même item, même sélection simulée, compare les payloads
    print("\n9) Comparaison BOT vs v2 (même arbre, premier choix partout) ---")
    target_item = None
    target_name = None

    # Priorité : menus type Kentucky avec au moins 3 groupes (PRODUIT / ACCOMPAGN / BOISSON)
    for cat_name, name, item in items_with_modgrps:
        modgrps = item.get("modgrps") or []
        if len(modgrps) < 3:
            continue
        if "Kentucky" in name and "Menu" in name:
            target_item = item
            target_name = name
            break
        if target_item is None:
            target_item = item
            target_name = name

    # Fallback : premier item avec au moins un groupe et des modifiers
    if target_item is None:
        for cat_name, name, item in items_with_modgrps:
            modgrps = item.get("modgrps") or []
            if not modgrps:
                continue
            if not any(g.get("modifiers") for g in modgrps):
                continue
            target_item = item
            target_name = name
            break
    if target_item and target_item.get("modgrps"):
        tree_bot = copy_module.deepcopy(target_item["modgrps"])
        tree_v2 = copy_module.deepcopy(target_item["modgrps"])
        _fill_tree_first_choice(tree_bot)
        _fill_tree_first_choice(tree_v2)
        payload_bot = modgrps_module.build_modgrps_from_tree(tree_bot)
        payload_v2 = [_build_modgrp_v2(g) for g in tree_v2]
        print(_compare_payloads(payload_bot, payload_v2, target_name))
        js_bot = json.dumps(payload_bot, ensure_ascii=False, indent=2)
        js_v2 = json.dumps(payload_v2, ensure_ascii=False, indent=2)
        print("\n   Payload BOT (extrait):")
        print(js_bot[:1200] + ("..." if len(js_bot) > 1200 else ""))
        print("\n   Payload v2 (extrait):")
        print(js_v2[:1200] + ("..." if len(js_v2) > 1200 else ""))
    else:
        print("   Aucun item avec modgrps utilisable pour la comparaison.")

    print("\n=== Fin test ===\n")


if __name__ == "__main__":
    main()
